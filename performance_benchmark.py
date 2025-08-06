#!/usr/bin/env python3
"""
Performance Benchmarking Suite for LEX AI System
🔱 JAI MAHAKAAL! Comprehensive performance testing and optimization validation
"""
import asyncio
import time
import json
import logging
import statistics
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import threading
import psutil
import requests

# Import optimization modules
from cache_manager import get_cache_manager
from db_pool_manager import get_db_pool
from response_optimizer import get_response_optimizer
from production_monitor import ProductionMonitor

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Individual benchmark test result"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    success: bool
    metrics: Dict[str, Any]
    error_message: Optional[str] = None
    
    @property
    def duration_ms(self) -> float:
        return self.duration_seconds * 1000

@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results"""
    suite_name: str
    start_time: datetime
    end_time: datetime
    total_duration: float
    tests_run: int
    tests_passed: int
    tests_failed: int
    overall_score: float
    results: List[BenchmarkResult]
    system_metrics: Dict[str, Any]
    
    @property
    def success_rate(self) -> float:
        if self.tests_run == 0:
            return 0.0
        return (self.tests_passed / self.tests_run) * 100

class PerformanceBenchmark:
    """Comprehensive performance benchmarking system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.cache_manager = get_cache_manager()
        self.db_pool = get_db_pool()
        self.response_optimizer = get_response_optimizer()
        self.monitor = ProductionMonitor()
        
        # Benchmark configuration
        self.benchmark_config = {
            'api_latency': {
                'endpoint': '/health',
                'method': 'GET',
                'timeout': 10,
                'target_response_time_ms': 500,
                'iterations': 50
            },
            'database_performance': {
                'query_count': 100,
                'concurrent_connections': 10,
                'target_query_time_ms': 50,
                'complex_query_target_ms': 100
            },
            'cache_efficiency': {
                'test_requests': 200,
                'target_hit_rate': 40,
                'cache_warmup_requests': 50
            },
            'load_capacity': {
                'concurrent_users': [1, 5, 10, 25, 50, 100],
                'requests_per_user': 10,
                'target_success_rate': 95,
                'max_response_time_ms': 5000
            },
            'model_performance': {
                'test_prompts': [
                    "What is artificial intelligence?",
                    "Write a Python function to calculate fibonacci numbers",
                    "Explain quantum computing in simple terms",
                    "Create a business plan for a coffee shop"
                ],
                'target_response_time_ms': 2000,
                'quality_threshold': 0.8
            }
        }
        
        # Test data
        self.test_queries = [
            "SELECT COUNT(*) FROM messages",
            "SELECT * FROM conversations WHERE user_id = 'test_user' ORDER BY created_at DESC LIMIT 10",
            "INSERT INTO messages (id, conversation_id, role, content) VALUES ('test_msg', 'test_conv', 'user', 'test content')",
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = 'test_conv'",
            "DELETE FROM messages WHERE id = 'test_msg'"
        ]
        
        self.results_history = []
        
        logger.info("✅ Performance Benchmark suite initialized")
    
    async def run_comprehensive_test(self) -> BenchmarkSuite:
        """Run complete benchmark suite"""
        logger.info("🔱 JAI MAHAKAAL! Starting Comprehensive Performance Benchmark 🔱")
        
        suite_start = datetime.utcnow()
        results = []
        
        # Capture initial system state
        initial_metrics = self._capture_system_metrics()
        
        # Define test suite
        test_suite = [
            ("API Latency Test", self.test_api_latency),
            ("Database Performance Test", self.test_db_performance),
            ("Cache Efficiency Test", self.test_cache_efficiency),
            ("Load Capacity Test", self.test_load_capacity),
            ("Model Performance Test", self.test_model_performance),
            ("Memory Usage Test", self.test_memory_usage),
            ("Optimization Effectiveness Test", self.test_optimization_effectiveness)
        ]
        
        # Run tests
        for test_name, test_func in test_suite:
            logger.info(f"🧪 Running {test_name}...")
            
            try:
                result = await test_func()
                results.append(result)
                
                if result.success:
                    logger.info(f"✅ {test_name} PASSED ({result.duration_ms:.1f}ms)")
                else:
                    logger.warning(f"⚠️ {test_name} FAILED: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"❌ {test_name} ERROR: {e}")
                results.append(BenchmarkResult(
                    test_name=test_name,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow(),
                    duration_seconds=0,
                    success=False,
                    metrics={},
                    error_message=str(e)
                ))
        
        # Capture final system state
        final_metrics = self._capture_system_metrics()
        
        # Calculate suite results
        suite_end = datetime.utcnow()
        total_duration = (suite_end - suite_start).total_seconds()
        tests_passed = sum(1 for r in results if r.success)
        tests_failed = len(results) - tests_passed
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(results)
        
        suite = BenchmarkSuite(
            suite_name="LEX Performance Comprehensive Test",
            start_time=suite_start,
            end_time=suite_end,
            total_duration=total_duration,
            tests_run=len(results),
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            overall_score=overall_score,
            results=results,
            system_metrics={
                'initial': initial_metrics,
                'final': final_metrics,
                'delta': self._calculate_metrics_delta(initial_metrics, final_metrics)
            }
        )
        
        # Save results
        self.results_history.append(suite)
        await self._save_benchmark_results(suite)
        
        logger.info("🎉 Comprehensive Performance Benchmark Complete!")
        logger.info(f"📊 Overall Score: {overall_score:.1f}/100")
        logger.info(f"📈 Success Rate: {suite.success_rate:.1f}%")
        
        return suite
    
    async def test_api_latency(self) -> BenchmarkResult:
        """Test API endpoint latency"""
        start_time = datetime.utcnow()
        config = self.benchmark_config['api_latency']
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        try:
            for i in range(config['iterations']):
                request_start = time.time()
                
                try:
                    response = requests.get(
                        f"{self.base_url}{config['endpoint']}",
                        timeout=config['timeout']
                    )
                    
                    request_duration = (time.time() - request_start) * 1000  # ms
                    response_times.append(request_duration)
                    
                    if response.status_code == 200:
                        successful_requests += 1
                    else:
                        failed_requests += 1
                        
                except Exception as e:
                    failed_requests += 1
                    logger.debug(f"API request failed: {e}")
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
            else:
                avg_response_time = p95_response_time = p99_response_time = 0
            
            success = (
                successful_requests > 0 and
                avg_response_time < config['target_response_time_ms'] and
                failed_requests / config['iterations'] < 0.05  # Less than 5% failure rate
            )
            
            metrics = {
                'total_requests': config['iterations'],
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'average_response_time_ms': round(avg_response_time, 2),
                'p95_response_time_ms': round(p95_response_time, 2),
                'p99_response_time_ms': round(p99_response_time, 2),
                'requests_per_second': round(successful_requests / duration, 2),
                'target_met': avg_response_time < config['target_response_time_ms']
            }
            
            return BenchmarkResult(
                test_name="API Latency Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                metrics=metrics
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return BenchmarkResult(
                test_name="API Latency Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                metrics={},
                error_message=str(e)
            )
    
    async def test_db_performance(self) -> BenchmarkResult:
        """Test database performance"""
        start_time = datetime.utcnow()
        config = self.benchmark_config['database_performance']
        
        try:
            query_times = []
            successful_queries = 0
            failed_queries = 0
            
            # Test basic queries
            for i in range(config['query_count']):
                for query in self.test_queries[:2]:  # Only SELECT queries for performance test
                    query_start = time.time()
                    
                    try:
                        self.db_pool.execute_query(query, fetch='all')
                        query_duration = (time.time() - query_start) * 1000  # ms
                        query_times.append(query_duration)
                        successful_queries += 1
                        
                    except Exception as e:
                        failed_queries += 1
                        logger.debug(f"Database query failed: {e}")
            
            # Test concurrent connections
            concurrent_times = []
            
            def execute_concurrent_query():
                query_start = time.time()
                try:
                    self.db_pool.execute_query("SELECT COUNT(*) FROM messages", fetch='one')
                    return (time.time() - query_start) * 1000
                except:
                    return None
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=config['concurrent_connections']) as executor:
                concurrent_futures = [executor.submit(execute_concurrent_query) for _ in range(50)]
                
                for future in concurrent.futures.as_completed(concurrent_futures):
                    result = future.result()
                    if result is not None:
                        concurrent_times.append(result)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            avg_query_time = statistics.mean(query_times) if query_times else 0
            avg_concurrent_time = statistics.mean(concurrent_times) if concurrent_times else 0
            
            success = (
                avg_query_time < config['target_query_time_ms'] and
                avg_concurrent_time < config['complex_query_target_ms'] and
                failed_queries / max(1, successful_queries + failed_queries) < 0.01
            )
            
            pool_stats = self.db_pool.get_pool_statistics()
            
            metrics = {
                'total_queries': successful_queries + failed_queries,
                'successful_queries': successful_queries,
                'failed_queries': failed_queries,
                'average_query_time_ms': round(avg_query_time, 2),
                'average_concurrent_query_time_ms': round(avg_concurrent_time, 2),
                'queries_per_second': round(successful_queries / duration, 2),
                'pool_utilization': pool_stats['pool_stats'],
                'target_met': avg_query_time < config['target_query_time_ms']
            }
            
            return BenchmarkResult(
                test_name="Database Performance Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                metrics=metrics
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return BenchmarkResult(
                test_name="Database Performance Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                metrics={},
                error_message=str(e)
            )
    
    async def test_cache_efficiency(self) -> BenchmarkResult:
        """Test cache system efficiency"""
        start_time = datetime.utcnow()
        config = self.benchmark_config['cache_efficiency']
        
        try:
            # Warm up cache
            warmup_prompts = [
                f"Test query {i} for cache warmup"
                for i in range(config['cache_warmup_requests'])
            ]
            
            for prompt in warmup_prompts:
                # Simulate caching the response
                test_response = {'response': f'Cached response for {prompt}'}
                self.cache_manager.cache_model_response(prompt, 'test_model', test_response)
            
            # Test cache hits
            cache_hits = 0
            cache_misses = 0
            total_requests = config['test_requests']
            
            for i in range(total_requests):
                prompt = f"Test query {i % config['cache_warmup_requests']} for cache warmup"
                
                cached_response = self.cache_manager.get_cached_response(prompt, 'test_model')
                
                if cached_response:
                    cache_hits += 1
                else:
                    cache_misses += 1
                    # Cache the response for next time
                    test_response = {'response': f'New cached response for {prompt}'}
                    self.cache_manager.cache_model_response(prompt, 'test_model', test_response)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            hit_rate = (cache_hits / total_requests) * 100
            cache_stats = self.cache_manager.get_cache_statistics()
            
            success = hit_rate >= config['target_hit_rate']
            
            metrics = {
                'total_requests': total_requests,
                'cache_hits': cache_hits,
                'cache_misses': cache_misses,
                'hit_rate_percent': round(hit_rate, 2),
                'target_hit_rate': config['target_hit_rate'],
                'cache_performance': cache_stats.get('performance_metrics', {}),
                'target_met': success
            }
            
            return BenchmarkResult(
                test_name="Cache Efficiency Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                metrics=metrics
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return BenchmarkResult(
                test_name="Cache Efficiency Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                metrics={},
                error_message=str(e)
            )
    
    async def test_load_capacity(self) -> BenchmarkResult:
        """Test system load capacity"""
        start_time = datetime.utcnow()
        config = self.benchmark_config['load_capacity']
        
        try:
            load_test_results = {}
            
            for user_count in config['concurrent_users']:
                logger.info(f"🔄 Testing {user_count} concurrent users...")
                
                async def simulate_user():
                    user_results = {
                        'successful_requests': 0,
                        'failed_requests': 0,
                        'response_times': []
                    }
                    
                    for _ in range(config['requests_per_user']):
                        request_start = time.time()
                        
                        try:
                            # Simulate API request
                            response = requests.get(
                                f"{self.base_url}/health",
                                timeout=config['max_response_time_ms'] / 1000
                            )
                            
                            request_duration = (time.time() - request_start) * 1000
                            user_results['response_times'].append(request_duration)
                            
                            if response.status_code == 200:
                                user_results['successful_requests'] += 1
                            else:
                                user_results['failed_requests'] += 1
                                
                        except Exception:
                            user_results['failed_requests'] += 1
                    
                    return user_results
                
                # Run concurrent users
                tasks = [simulate_user() for _ in range(user_count)]
                user_results = await asyncio.gather(*tasks)
                
                # Aggregate results
                total_successful = sum(r['successful_requests'] for r in user_results)
                total_failed = sum(r['failed_requests'] for r in user_results)
                all_response_times = []
                
                for r in user_results:
                    all_response_times.extend(r['response_times'])
                
                total_requests = total_successful + total_failed
                success_rate = (total_successful / max(1, total_requests)) * 100
                avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
                
                load_test_results[user_count] = {
                    'total_requests': total_requests,
                    'successful_requests': total_successful,
                    'failed_requests': total_failed,
                    'success_rate': round(success_rate, 2),
                    'average_response_time_ms': round(avg_response_time, 2),
                    'target_success_rate_met': success_rate >= config['target_success_rate'],
                    'target_response_time_met': avg_response_time <= config['max_response_time_ms']
                }
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Determine overall success
            max_successful_users = 0
            for user_count, results in load_test_results.items():
                if (results['target_success_rate_met'] and 
                    results['target_response_time_met']):
                    max_successful_users = user_count
            
            success = max_successful_users >= min(config['concurrent_users'])
            
            metrics = {
                'load_test_results': load_test_results,
                'max_concurrent_users_supported': max_successful_users,
                'target_concurrent_users': max(config['concurrent_users']),
                'load_capacity_score': (max_successful_users / max(config['concurrent_users'])) * 100
            }
            
            return BenchmarkResult(
                test_name="Load Capacity Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                metrics=metrics
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return BenchmarkResult(
                test_name="Load Capacity Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                metrics={},
                error_message=str(e)
            )
    
    async def test_model_performance(self) -> BenchmarkResult:
        """Test model response performance"""
        start_time = datetime.utcnow()
        config = self.benchmark_config['model_performance']
        
        try:
            model_results = []
            
            for prompt in config['test_prompts']:
                prompt_start = time.time()
                
                try:
                    # Test optimized response
                    response = await self.response_optimizer.get_optimized_response(
                        prompt=prompt,
                        context={'priority': 'speed'}
                    )
                    
                    response_time = (time.time() - prompt_start) * 1000  # ms
                    
                    model_results.append({
                        'prompt': prompt[:50] + '...',
                        'response_time_ms': round(response_time, 2),
                        'confidence': response.get('confidence', 0.0),
                        'model_used': response.get('model_used', 'unknown'),
                        'optimization_applied': response.get('optimization_applied', False),
                        'target_met': response_time <= config['target_response_time_ms'],
                        'quality_met': response.get('confidence', 0.0) >= config['quality_threshold']
                    })
                    
                except Exception as e:
                    model_results.append({
                        'prompt': prompt[:50] + '...',
                        'error': str(e),
                        'target_met': False,
                        'quality_met': False
                    })
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            successful_responses = sum(1 for r in model_results if 'error' not in r)
            target_met_count = sum(1 for r in model_results if r.get('target_met', False))
            quality_met_count = sum(1 for r in model_results if r.get('quality_met', False))
            
            avg_response_time = statistics.mean([
                r['response_time_ms'] for r in model_results 
                if 'response_time_ms' in r
            ]) if any('response_time_ms' in r for r in model_results) else 0
            
            success = (
                successful_responses == len(config['test_prompts']) and
                target_met_count >= len(config['test_prompts']) * 0.8 and
                quality_met_count >= len(config['test_prompts']) * 0.8
            )
            
            metrics = {
                'total_prompts': len(config['test_prompts']),
                'successful_responses': successful_responses,
                'average_response_time_ms': round(avg_response_time, 2),
                'target_response_time_ms': config['target_response_time_ms'],
                'target_met_count': target_met_count,
                'quality_met_count': quality_met_count,
                'model_results': model_results,
                'optimization_metrics': self.response_optimizer.get_optimization_metrics()
            }
            
            return BenchmarkResult(
                test_name="Model Performance Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                metrics=metrics
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return BenchmarkResult(
                test_name="Model Performance Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                metrics={},
                error_message=str(e)
            )
    
    async def test_memory_usage(self) -> BenchmarkResult:
        """Test memory usage and efficiency"""
        start_time = datetime.utcnow()
        
        try:
            import psutil
            process = psutil.Process()
            
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate memory-intensive operations
            test_data = []
            for i in range(1000):
                # Create some test data
                large_dict = {
                    f'key_{j}': f'value_{j}_' * 100 
                    for j in range(100)
                }
                test_data.append(large_dict)
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Clear test data
            test_data.clear()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            memory_growth = peak_memory - initial_memory
            memory_released = peak_memory - final_memory
            memory_efficiency = (memory_released / memory_growth) * 100 if memory_growth > 0 else 100
            
            success = (
                memory_growth < 500 and  # Less than 500MB growth
                memory_efficiency > 80   # More than 80% memory released
            )
            
            metrics = {
                'initial_memory_mb': round(initial_memory, 2),
                'peak_memory_mb': round(peak_memory, 2),
                'final_memory_mb': round(final_memory, 2),
                'memory_growth_mb': round(memory_growth, 2),
                'memory_released_mb': round(memory_released, 2),
                'memory_efficiency_percent': round(memory_efficiency, 2),
                'memory_usage_acceptable': memory_growth < 500
            }
            
            return BenchmarkResult(
                test_name="Memory Usage Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                metrics=metrics
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return BenchmarkResult(
                test_name="Memory Usage Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                metrics={},
                error_message=str(e)
            )
    
    async def test_optimization_effectiveness(self) -> BenchmarkResult:
        """Test overall optimization effectiveness"""
        start_time = datetime.utcnow()
        
        try:
            # Get optimization metrics
            cache_stats = self.cache_manager.get_cache_statistics()
            pool_stats = self.db_pool.get_pool_statistics()
            optimizer_metrics = self.response_optimizer.get_optimization_metrics()
            
            # Calculate optimization scores
            cache_score = min(100, cache_stats['performance_metrics'].get('hit_rate_percent', 0) * 2)
            db_score = min(100, 100 - (pool_stats['query_stats'].get('average_query_time_ms', 100) / 10))
            optimizer_score = optimizer_metrics['performance_improvements'].get('optimization_effectiveness', 0)
            
            overall_optimization_score = (cache_score + db_score + optimizer_score) / 3
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            success = overall_optimization_score >= 70  # 70% optimization effectiveness
            
            metrics = {
                'cache_optimization_score': round(cache_score, 2),
                'database_optimization_score': round(db_score, 2),
                'response_optimization_score': round(optimizer_score, 2),
                'overall_optimization_score': round(overall_optimization_score, 2),
                'cache_stats': cache_stats,
                'pool_stats': pool_stats,
                'optimizer_metrics': optimizer_metrics,
                'optimization_target_met': success
            }
            
            return BenchmarkResult(
                test_name="Optimization Effectiveness Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                metrics=metrics
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return BenchmarkResult(
                test_name="Optimization Effectiveness Test",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                metrics={},
                error_message=str(e)
            )
    
    def _capture_system_metrics(self) -> Dict[str, Any]:
        """Capture current system metrics"""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'timestamp': datetime.utcnow().isoformat()
            }
        except:
            return {'timestamp': datetime.utcnow().isoformat()}
    
    def _calculate_metrics_delta(self, initial: Dict, final: Dict) -> Dict[str, Any]:
        """Calculate change in metrics"""
        delta = {}
        
        for key in ['cpu_percent', 'memory_percent', 'disk_usage_percent']:
            if key in initial and key in final:
                delta[f'{key}_change'] = round(final[key] - initial[key], 2)
        
        return delta
    
    def _calculate_overall_score(self, results: List[BenchmarkResult]) -> float:
        """Calculate overall benchmark score"""
        if not results:
            return 0.0
        
        # Weight different test types
        test_weights = {
            'API Latency Test': 0.25,
            'Database Performance Test': 0.20,
            'Cache Efficiency Test': 0.15,
            'Load Capacity Test': 0.20,
            'Model Performance Test': 0.15,
            'Memory Usage Test': 0.03,
            'Optimization Effectiveness Test': 0.02
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for result in results:
            weight = test_weights.get(result.test_name, 0.1)
            score = 100 if result.success else 0
            
            weighted_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            return weighted_score / total_weight
        else:
            return sum(100 if r.success else 0 for r in results) / len(results)
    
    async def _save_benchmark_results(self, suite: BenchmarkSuite):
        """Save benchmark results to file"""
        try:
            results_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert to serializable format
            suite_dict = asdict(suite)
            
            # Handle datetime serialization
            def datetime_handler(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(results_file, 'w') as f:
                json.dump(suite_dict, f, indent=2, default=datetime_handler)
            
            logger.info(f"📄 Benchmark results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save benchmark results: {e}")
    
    def generate_performance_report(self, suite: BenchmarkSuite) -> str:
        """Generate comprehensive performance report"""
        report_lines = [
            "=" * 80,
            "🔱 LEX AI PERFORMANCE BENCHMARK REPORT 🔱",
            "=" * 80,
            f"Suite: {suite.suite_name}",
            f"Executed: {suite.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Duration: {suite.total_duration:.2f} seconds",
            f"Overall Score: {suite.overall_score:.1f}/100",
            f"Success Rate: {suite.success_rate:.1f}%",
            "",
            "📊 TEST RESULTS:",
            "-" * 40
        ]
        
        for result in suite.results:
            status_icon = "✅" if result.success else "❌"
            report_lines.append(
                f"{status_icon} {result.test_name}: {result.duration_ms:.1f}ms"
            )
            
            if result.success and result.metrics:
                # Add key metrics
                for key, value in result.metrics.items():
                    if isinstance(value, (int, float)) and not key.endswith('_results'):
                        report_lines.append(f"    {key}: {value}")
        
        report_lines.extend([
            "",
            "🎯 PERFORMANCE TARGETS:",
            "-" * 40,
            "• API Response Time: < 500ms",
            "• Database Query Time: < 50ms",
            "• Cache Hit Rate: > 40%",
            "• Load Capacity: > 50 concurrent users",
            "• Model Response: < 2000ms",
            "",
            "💡 RECOMMENDATIONS:",
            "-" * 40
        ])
        
        # Add recommendations based on results
        recommendations = self._generate_recommendations(suite)
        for rec in recommendations:
            report_lines.append(f"• {rec}")
        
        report_lines.extend([
            "",
            "=" * 80,
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(self, suite: BenchmarkSuite) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        for result in suite.results:
            if not result.success:
                if result.test_name == "API Latency Test":
                    recommendations.append("Consider optimizing API endpoints or adding caching")
                elif result.test_name == "Database Performance Test":
                    recommendations.append("Consider adding database indexes or increasing pool size")
                elif result.test_name == "Cache Efficiency Test":
                    recommendations.append("Consider tuning cache TTL or increasing cache size")
                elif result.test_name == "Load Capacity Test":
                    recommendations.append("Consider horizontal scaling or optimizing resource usage")
                elif result.test_name == "Model Performance Test":
                    recommendations.append("Consider using faster models for simple queries")
        
        if suite.overall_score < 80:
            recommendations.append("Overall system performance needs optimization")
        
        if not recommendations:
            recommendations.append("System performance is excellent! Consider stress testing with higher loads")
        
        return recommendations

def main():
    """CLI interface for performance benchmarking"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LEX Performance Benchmark")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for testing")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive test suite")
    parser.add_argument("--quick", action="store_true", help="Run quick performance test")
    parser.add_argument("--report", action="store_true", help="Generate performance report")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    benchmark = PerformanceBenchmark(args.url)
    
    async def run_benchmark():
        if args.comprehensive:
            suite = await benchmark.run_comprehensive_test()
            
            if args.report:
                report = benchmark.generate_performance_report(suite)
                print(report)
                
                # Save report to file
                with open(f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
                    f.write(report)
        
        elif args.quick:
            # Run subset of tests
            api_result = await benchmark.test_api_latency()
            db_result = await benchmark.test_db_performance()
            
            print(f"API Latency: {'PASS' if api_result.success else 'FAIL'} ({api_result.duration_ms:.1f}ms)")
            print(f"Database Performance: {'PASS' if db_result.success else 'FAIL'} ({db_result.duration_ms:.1f}ms)")
        
        else:
            parser.print_help()
    
    asyncio.run(run_benchmark())

if __name__ == "__main__":
    main()