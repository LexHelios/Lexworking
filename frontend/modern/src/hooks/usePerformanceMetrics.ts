import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';

// Types
interface PerformanceMetrics {
  cache_hit_rate: number;
  average_db_query_time_ms: number;
  total_cost_savings_usd: number;
  optimization_effectiveness: number;
  requests_processed: number;
  active_connections: number;
  total_messages_sent: number;
  avg_stream_time: number;
}

interface CacheStats {
  total_requests: number;
  cache_hits: number;
  cache_misses: number;
  hit_rate_percent: number;
  total_cost_savings_usd: number;
  average_time_saved_seconds: number;
}

interface DatabaseStats {
  total_connections_created: number;
  active_connections: number;
  available_connections: number;
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  average_query_time_ms: number;
  success_rate_percent: number;
}

interface OptimizationMetrics {
  total_requests: number;
  cache_hits: number;
  fast_model_uses: number;
  optimization_effectiveness: number;
}

interface DetailedPerformanceData {
  timestamp: string;
  cache_performance: {
    cache_stats: CacheStats;
    performance_metrics: PerformanceMetrics;
  };
  database_performance: {
    pool_stats: DatabaseStats;
    query_stats: DatabaseStats;
  };
  optimization_metrics: {
    response_optimization: OptimizationMetrics;
    performance_improvements: {
      optimization_effectiveness: number;
      total_cost_saved_usd: number;
    };
  };
  performance_summary: PerformanceMetrics;
}

interface UsePerformanceMetricsReturn {
  performanceData: PerformanceMetrics | null;
  detailedData: DetailedPerformanceData | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
  lastUpdated: Date | null;
}

const usePerformanceMetrics = (
  refreshInterval: number = 30000, // 30 seconds
  enableAutoRefresh: boolean = true
): UsePerformanceMetricsReturn => {
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Fetch performance metrics
  const {
    data: detailedData,
    isLoading,
    error,
    refetch
  } = useQuery<DetailedPerformanceData>(
    'performanceMetrics',
    async () => {
      try {
        const response = await axios.get('/api/v1/performance', {
          timeout: 10000,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });
        
        setLastUpdated(new Date());
        return response.data;
      } catch (err: any) {
        if (err.response?.status === 404) {
          // Fallback to basic health check if performance endpoint not available
          const healthResponse = await axios.get('/health');
          
          // Transform health data to performance metrics format
          const healthData = healthResponse.data;
          const performanceOptimization = healthData.performance_optimization || {};
          const performanceMetrics = healthData.performance_metrics || {};
          
          const fallbackData: DetailedPerformanceData = {
            timestamp: new Date().toISOString(),
            cache_performance: {
              cache_stats: {
                total_requests: 0,
                cache_hits: 0,
                cache_misses: 0,
                hit_rate_percent: performanceOptimization.cache_hit_rate || 0,
                total_cost_savings_usd: performanceMetrics.total_cost_saved_usd || 0,
                average_time_saved_seconds: 0
              },
              performance_metrics: {
                cache_hit_rate: performanceOptimization.cache_hit_rate || 0,
                average_db_query_time_ms: performanceMetrics.average_query_time_ms || 0,
                total_cost_savings_usd: performanceMetrics.total_cost_saved_usd || 0,
                optimization_effectiveness: performanceMetrics.optimization_score || 0,
                requests_processed: performanceMetrics.requests_processed || 0,
                active_connections: performanceOptimization.database_pool_active || 0,
                total_messages_sent: 0,
                avg_stream_time: 0
              }
            },
            database_performance: {
              pool_stats: {
                total_connections_created: 0,
                active_connections: performanceOptimization.database_pool_active || 0,
                available_connections: performanceOptimization.database_pool_available || 0,
                total_queries: 0,
                successful_queries: 0,
                failed_queries: 0,
                average_query_time_ms: performanceMetrics.average_query_time_ms || 0,
                success_rate_percent: 100
              },
              query_stats: {
                total_connections_created: 0,
                active_connections: 0,
                available_connections: 0,
                total_queries: 0,
                successful_queries: 0,
                failed_queries: 0,
                average_query_time_ms: performanceMetrics.average_query_time_ms || 0,
                success_rate_percent: 100
              }
            },
            optimization_metrics: {
              response_optimization: {
                total_requests: performanceMetrics.requests_processed || 0,
                cache_hits: 0,
                fast_model_uses: 0,
                optimization_effectiveness: performanceMetrics.optimization_score || 0
              },
              performance_improvements: {
                optimization_effectiveness: performanceMetrics.optimization_score || 0,
                total_cost_saved_usd: performanceMetrics.total_cost_saved_usd || 0
              }
            },
            performance_summary: {
              cache_hit_rate: performanceOptimization.cache_hit_rate || 0,
              average_db_query_time_ms: performanceMetrics.average_query_time_ms || 0,
              total_cost_savings_usd: performanceMetrics.total_cost_saved_usd || 0,
              optimization_effectiveness: performanceMetrics.optimization_score || 0,
              requests_processed: performanceMetrics.requests_processed || 0,
              active_connections: performanceOptimization.database_pool_active || 0,
              total_messages_sent: 0,
              avg_stream_time: 0
            }
          };
          
          setLastUpdated(new Date());
          return fallbackData;
        }
        
        throw err;
      }
    },
    {
      refetchInterval: enableAutoRefresh ? refreshInterval : false,
      refetchIntervalInBackground: false,
      retry: 2,
      retryDelay: 5000,
      onError: (err: any) => {
        console.error('❌ Performance metrics fetch error:', err);
      }
    }
  );

  // Extract simplified performance data
  const performanceData: PerformanceMetrics | null = detailedData?.performance_summary || null;

  // Enhanced refetch with error handling
  const enhancedRefetch = async () => {
    try {
      await refetch();
    } catch (err) {
      console.error('❌ Manual refetch failed:', err);
    }
  };

  return {
    performanceData,
    detailedData,
    isLoading,
    error: error ? String(error) : null,
    refetch: enhancedRefetch,
    lastUpdated
  };
};

export default usePerformanceMetrics;