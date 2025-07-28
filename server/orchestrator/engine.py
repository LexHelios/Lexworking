"""
LexOS Vibe Coder - vLLM Engine Wrapper
High-performance inference engine with H100 GPU optimization
"""
import asyncio
import aiohttp
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import time
from prometheus_client import Counter, Histogram, Gauge
import re

from ..settings import settings

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('orchestrator_requests_total', 'Total orchestrator requests', ['model', 'status'])
REQUEST_LATENCY = Histogram('orchestrator_request_latency_seconds', 'Orchestrator request latency', ['model'])
CIRCUIT_BREAKER_STATE = Gauge('orchestrator_circuit_breaker_state', 'Circuit breaker state (1=open, 0=closed)', ['model'])

# Orchestration trace log (in-memory, for demo; use persistent store in prod)
orchestration_traces = []

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_time=60):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = {}
        self.open_until = {}

    def record_failure(self, model):
        self.failures[model] = self.failures.get(model, 0) + 1
        if self.failures[model] >= self.failure_threshold:
            self.open_until[model] = time.time() + self.recovery_time
            CIRCUIT_BREAKER_STATE.labels(model=model).set(1)

    def record_success(self, model):
        self.failures[model] = 0
        self.open_until[model] = 0
        CIRCUIT_BREAKER_STATE.labels(model=model).set(0)

    def is_open(self, model):
        return time.time() < self.open_until.get(model, 0)

circuit_breaker = CircuitBreaker()

class VLLMEngine:
    """
    vLLM Engine wrapper for high-performance inference
    
    Features:
    - Multiple model support with automatic routing
    - H100 GPU optimization
    - Concurrent request handling
    - Model health monitoring
    - Automatic failover
    - Prometheus metrics
    - Circuit breaker for unhealthy models
    - Orchestration trace logging
    """
    
    def __init__(self):
        self.base_url = settings.vllm_url
        self.available_models = settings.VLLM_MODELS
        self.default_model = settings.DEFAULT_MODEL
        
        # Model status tracking
        self.model_status = {}
        self.model_performance = {}
        
        # Request tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0
        
        # Connection pool
        self.session = None
        
        logger.info(f"🚀 vLLM Engine initialized - Base URL: {self.base_url}")
    
    async def initialize(self) -> None:
        """Initialize vLLM engine and check model availability"""
        try:
            # Create aiohttp session with optimized settings
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes for long generations
            connector = aiohttp.TCPConnector(
                limit=100,  # Connection pool size
                limit_per_host=50,
                keepalive_timeout=30
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"Content-Type": "application/json"}
            )
            
            # Check vLLM server health
            await self._check_server_health()
            
            # Initialize model status
            for model in self.available_models:
                await self._check_model_status(model)
            
            logger.info("✅ vLLM Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ vLLM Engine initialization error: {e}")
            raise
    
    def score_models(self, messages: List[Dict[str, str]], user_id: Optional[str] = None, task_type: Optional[str] = None) -> List[str]:
        """
        Score and rank models for a given request. Extend this logic for user/task personalization.
        Returns a list of model names ordered by score (best first).
        """
        # Example: prioritize based on task_type or user_id (stub logic)
        if task_type == "code":
            preferred = [m for m in self.available_models if "mixtral" in m.lower() or "llama" in m.lower()]
        elif task_type == "creative":
            preferred = [m for m in self.available_models if "gemma" in m.lower() or "llama" in m.lower()]
        else:
            preferred = self.available_models
        # Fallback: return all models in default order
        return preferred + [m for m in self.available_models if m not in preferred]

    async def generate_text(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stream: bool = False,
        ensemble: bool = False,
        user_id: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> str:
        """
        Generate text using vLLM
        Adds Prometheus metrics, input validation, circuit breaker, orchestration trace logging, and ensembling.
        """
        start_time = time.time()
        status = "success"
        orchestration_trace = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "messages": messages,
            "params": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stream": stream,
                "ensemble": ensemble,
                "user_id": user_id,
                "task_type": task_type
            },
            "result": None,
            "error": None
        }
        try:
            # Input validation
            if not isinstance(model_name, str) or not re.match(r"^[\w\-/]+$", model_name):
                raise ValueError("Invalid model name")
            if not isinstance(messages, list) or not all(isinstance(m, dict) for m in messages):
                raise ValueError("Invalid messages format")
            # Automatic model selection
            if model_name == "auto":
                ranked_models = self.score_models(messages, user_id, task_type)
                model_name = ranked_models[0]
            if ensemble:
                ranked_models = self.score_models(messages, user_id, task_type)[:2]  # Ensemble top 2
                results = []
                for m in ranked_models:
                    try:
                        result = await self.generate_text(
                            model_name=m,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            frequency_penalty=frequency_penalty,
                            presence_penalty=presence_penalty,
                            stream=stream,
                            ensemble=False,
                            user_id=user_id,
                            task_type=task_type
                        )
                        results.append(result)
                    except Exception as e:
                        logger.warning(f"Ensemble model {m} failed: {e}")
                # Simple ensembling: majority vote or concatenate
                if results:
                    # Majority vote (if all agree), else concatenate
                    if all(r == results[0] for r in results):
                        response_text = results[0]
                    else:
                        response_text = "\n---\n".join(results)
                else:
                    raise Exception("No ensemble results available")
                orchestration_trace["result"] = response_text
                orchestration_traces.append(orchestration_trace)
                return response_text
            if model_name not in self.available_models:
                logger.warning(f"⚠️ Model {model_name} not available, using default: {self.default_model}")
                model_name = self.default_model
            # Circuit breaker
            if circuit_breaker.is_open(model_name):
                status = "circuit_open"
                raise Exception(f"Circuit breaker open for model {model_name}")
            # Check model health
            if not await self._is_model_healthy(model_name):
                healthy_model = await self._find_healthy_model()
                if healthy_model:
                    logger.warning(f"⚠️ Model {model_name} unhealthy, using: {healthy_model}")
                    model_name = healthy_model
                else:
                    status = "no_healthy_model"
                    raise Exception("No healthy models available")
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stream": stream
            }
            if stream:
                response_text = await self._generate_streaming(payload)
            else:
                response_text = await self._generate_non_streaming(payload)
            response_time = time.time() - start_time
            self._update_metrics(model_name, response_time, True)
            circuit_breaker.record_success(model_name)
            REQUEST_COUNT.labels(model=model_name, status="success").inc()
            REQUEST_LATENCY.labels(model=model_name).observe(response_time)
            orchestration_trace["result"] = response_text
            orchestration_traces.append(orchestration_trace)
            logger.debug(f"🚀 Generated {len(response_text)} chars in {response_time:.3f}s using {model_name}")
            return response_text
        except Exception as e:
            response_time = time.time() - start_time
            self._update_metrics(model_name, response_time, False)
            circuit_breaker.record_failure(model_name)
            REQUEST_COUNT.labels(model=model_name, status="failure").inc()
            REQUEST_LATENCY.labels(model=model_name).observe(response_time)
            orchestration_trace["error"] = str(e)
            orchestration_traces.append(orchestration_trace)
            logger.error(f"❌ Text generation error: {e}")
            raise
    
    async def _generate_non_streaming(self, payload: Dict[str, Any]) -> str:
        """Generate text without streaming"""
        try:
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract generated text
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        raise Exception("No choices in response")
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Non-streaming generation error: {e}")
            raise
    
    async def _generate_streaming(self, payload: Dict[str, Any]) -> str:
        """Generate text with streaming (for future implementation)"""
        # For now, fallback to non-streaming
        # In production, implement proper streaming with Server-Sent Events
        payload["stream"] = False
        return await self._generate_non_streaming(payload)
    
    async def _check_server_health(self) -> bool:
        """Check if vLLM server is healthy"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    logger.info("✅ vLLM server is healthy")
                    return True
                else:
                    logger.warning(f"⚠️ vLLM server health check failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ vLLM server health check error: {e}")
            return False
    
    async def _check_model_status(self, model_name: str) -> bool:
        """Check if a specific model is available and healthy"""
        try:
            # Test with a simple request
            test_payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=test_payload) as response:
                if response.status == 200:
                    self.model_status[model_name] = {
                        "status": "healthy",
                        "last_check": datetime.now().isoformat(),
                        "response_time": response.headers.get("X-Response-Time", "unknown")
                    }
                    logger.debug(f"✅ Model {model_name} is healthy")
                    return True
                else:
                    self.model_status[model_name] = {
                        "status": "unhealthy",
                        "last_check": datetime.now().isoformat(),
                        "error": f"HTTP {response.status}"
                    }
                    logger.warning(f"⚠️ Model {model_name} is unhealthy: {response.status}")
                    return False
                    
        except Exception as e:
            self.model_status[model_name] = {
                "status": "error",
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }
            logger.error(f"❌ Model {model_name} check error: {e}")
            return False
    
    async def _is_model_healthy(self, model_name: str) -> bool:
        """Check if model is currently healthy"""
        status = self.model_status.get(model_name, {})
        return status.get("status") == "healthy"
    
    async def _find_healthy_model(self) -> Optional[str]:
        """Find the first healthy model available"""
        for model in self.available_models:
            if await self._is_model_healthy(model):
                return model
        
        # If no models are marked as healthy, try to check them
        for model in self.available_models:
            if await self._check_model_status(model):
                return model
        
        return None
    
    def _update_metrics(self, model_name: str, response_time: float, success: bool) -> None:
        """Update performance metrics"""
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Update average response time
        if self.total_requests == 1:
            self.average_response_time = response_time
        else:
            alpha = 0.1  # Smoothing factor
            self.average_response_time = (
                alpha * response_time + 
                (1 - alpha) * self.average_response_time
            )
        
        # Update model-specific performance
        if model_name not in self.model_performance:
            self.model_performance[model_name] = {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "avg_response_time": 0.0
            }
        
        perf = self.model_performance[model_name]
        perf["requests"] += 1
        
        if success:
            perf["successes"] += 1
        else:
            perf["failures"] += 1
        
        # Update model average response time
        if perf["requests"] == 1:
            perf["avg_response_time"] = response_time
        else:
            alpha = 0.1
            perf["avg_response_time"] = (
                alpha * response_time + 
                (1 - alpha) * perf["avg_response_time"]
            )
    
    async def get_model_list(self) -> List[Dict[str, Any]]:
        """Get list of available models with their status"""
        models = []
        
        for model_name in self.available_models:
            status = self.model_status.get(model_name, {"status": "unknown"})
            performance = self.model_performance.get(model_name, {})
            
            model_info = {
                "name": model_name,
                "status": status.get("status", "unknown"),
                "last_check": status.get("last_check", "never"),
                "performance": {
                    "requests": performance.get("requests", 0),
                    "success_rate": (
                        performance.get("successes", 0) / performance.get("requests", 1)
                        if performance.get("requests", 0) > 0 else 0.0
                    ),
                    "avg_response_time": performance.get("avg_response_time", 0.0)
                }
            }
            models.append(model_info)
        
        return models
    
    async def get_engine_statistics(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics"""
        success_rate = (
            self.successful_requests / self.total_requests 
            if self.total_requests > 0 else 0.0
        )
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "average_response_time": self.average_response_time,
            "available_models": len(self.available_models),
            "healthy_models": sum(1 for status in self.model_status.values() 
                                if status.get("status") == "healthy"),
            "default_model": self.default_model,
            "base_url": self.base_url
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            # Check server health
            server_healthy = await self._check_server_health()
            
            # Check model health
            healthy_models = 0
            for model in self.available_models:
                if await self._check_model_status(model):
                    healthy_models += 1
            
            status = "healthy" if server_healthy and healthy_models > 0 else "unhealthy"
            
            return {
                "status": status,
                "server_healthy": server_healthy,
                "healthy_models": healthy_models,
                "total_models": len(self.available_models),
                "statistics": await self.get_engine_statistics(),
                "model_status": self.model_status.copy()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "server_healthy": False,
                "healthy_models": 0
            }
    
    async def shutdown(self) -> None:
        """Shutdown the engine and close connections"""
        try:
            if self.session:
                await self.session.close()
                logger.info("🚀 vLLM Engine shutdown complete")
        except Exception as e:
            logger.error(f"❌ vLLM Engine shutdown error: {e}")

# Global vLLM engine instance
vllm_engine = VLLMEngine()
