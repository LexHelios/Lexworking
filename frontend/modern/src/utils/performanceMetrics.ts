// Performance monitoring utilities for the LEX frontend

interface PerformanceEntry {
  name: string;
  startTime: number;
  duration: number;
  entryType: string;
}

interface WebVitals {
  FCP: number; // First Contentful Paint
  LCP: number; // Largest Contentful Paint  
  FID: number; // First Input Delay
  CLS: number; // Cumulative Layout Shift
  TTFB: number; // Time to First Byte
}

class PerformanceMonitor {
  private metrics: Map<string, number> = new Map();
  private observers: Map<string, PerformanceObserver> = new Map();

  constructor() {
    this.initializeObservers();
  }

  private initializeObservers() {
    // Observe navigation timing
    if ('PerformanceObserver' in window) {
      try {
        const navObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.entryType === 'navigation') {
              const navEntry = entry as PerformanceNavigationTiming;
              this.metrics.set('domContentLoaded', navEntry.domContentLoadedEventStart);
              this.metrics.set('loadComplete', navEntry.loadEventEnd);
              this.metrics.set('ttfb', navEntry.responseStart);
            }
          }
        });
        navObserver.observe({ entryTypes: ['navigation'] });
        this.observers.set('navigation', navObserver);
      } catch (e) {
        console.warn('Navigation timing observer not supported');
      }

      // Observe paint timing
      try {
        const paintObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              this.metrics.set('FCP', entry.startTime);
            } else if (entry.name === 'first-paint') {
              this.metrics.set('FP', entry.startTime);
            }
          }
        });
        paintObserver.observe({ entryTypes: ['paint'] });
        this.observers.set('paint', paintObserver);
      } catch (e) {
        console.warn('Paint timing observer not supported');
      }

      // Observe largest contentful paint
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          this.metrics.set('LCP', lastEntry.startTime);
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        this.observers.set('lcp', lcpObserver);
      } catch (e) {
        console.warn('LCP observer not supported');
      }

      // Observe layout shifts
      try {
        const clsObserver = new PerformanceObserver((list) => {
          let clsValue = this.metrics.get('CLS') || 0;
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += (entry as any).value;
            }
          }
          this.metrics.set('CLS', clsValue);
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
        this.observers.set('cls', clsObserver);
      } catch (e) {
        console.warn('CLS observer not supported');
      }
    }
  }

  // Track custom performance metrics
  markStart(name: string): void {
    performance.mark(`${name}-start`);
  }

  markEnd(name: string): number {
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    const entries = performance.getEntriesByName(name, 'measure');
    if (entries.length > 0) {
      const duration = entries[entries.length - 1].duration;
      this.metrics.set(name, duration);
      return duration;
    }
    return 0;
  }

  // Get all current metrics
  getMetrics(): Record<string, number> {
    return Object.fromEntries(this.metrics);
  }

  // Get Web Vitals
  getWebVitals(): Partial<WebVitals> {
    return {
      FCP: this.metrics.get('FCP'),
      LCP: this.metrics.get('LCP'),
      CLS: this.metrics.get('CLS'),
      TTFB: this.metrics.get('ttfb'),
      FID: this.metrics.get('FID'),
    };
  }

  // Track user interactions
  trackInteraction(name: string, startTime: number = performance.now()): () => void {
    const endTime = performance.now();
    this.metrics.set(`interaction-${name}`, endTime - startTime);
    
    return () => {
      const finalTime = performance.now();
      this.metrics.set(`interaction-${name}-total`, finalTime - startTime);
    };
  }

  // Track API call performance
  trackApiCall(endpoint: string, duration: number, success: boolean): void {
    this.metrics.set(`api-${endpoint}-duration`, duration);
    this.metrics.set(`api-${endpoint}-success`, success ? 1 : 0);
  }

  // Get performance report
  generateReport(): {
    timestamp: string;
    metrics: Record<string, number>;
    webVitals: Partial<WebVitals>;
    grade: string;
  } {
    const webVitals = this.getWebVitals();
    
    // Calculate performance grade
    let score = 100;
    
    if (webVitals.FCP && webVitals.FCP > 2000) score -= 20;
    if (webVitals.LCP && webVitals.LCP > 4000) score -= 30;
    if (webVitals.CLS && webVitals.CLS > 0.25) score -= 25;
    if (webVitals.FID && webVitals.FID > 300) score -= 25;

    const grade = score >= 90 ? 'A' : score >= 75 ? 'B' : score >= 60 ? 'C' : score >= 40 ? 'D' : 'F';

    return {
      timestamp: new Date().toISOString(),
      metrics: this.getMetrics(),
      webVitals,
      grade,
    };
  }

  // Clean up observers
  disconnect(): void {
    for (const observer of this.observers.values()) {
      observer.disconnect();
    }
    this.observers.clear();
  }
}

// Global instance
export const performanceMonitor = new PerformanceMonitor();

// Utility functions
export const measureAsync = async <T>(
  name: string, 
  asyncFn: () => Promise<T>
): Promise<T> => {
  performanceMonitor.markStart(name);
  try {
    const result = await asyncFn();
    performanceMonitor.markEnd(name);
    return result;
  } catch (error) {
    performanceMonitor.markEnd(name);
    throw error;
  }
};

export const measureSync = <T>(name: string, syncFn: () => T): T => {
  performanceMonitor.markStart(name);
  try {
    const result = syncFn();
    performanceMonitor.markEnd(name);
    return result;
  } catch (error) {
    performanceMonitor.markEnd(name);
    throw error;
  }
};

// Hook for React components
export const usePerformanceTracking = (componentName: string) => {
  const trackRender = () => {
    performanceMonitor.markStart(`${componentName}-render`);
    return () => performanceMonitor.markEnd(`${componentName}-render`);
  };

  const trackInteraction = (interactionName: string) => {
    return performanceMonitor.trackInteraction(`${componentName}-${interactionName}`);
  };

  return { trackRender, trackInteraction };
};

export default performanceMonitor;