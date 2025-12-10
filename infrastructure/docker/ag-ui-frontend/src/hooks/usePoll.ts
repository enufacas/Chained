/**
 * usePoll - Smart polling hook with exponential backoff
 * 
 * Improves UI responsiveness by:
 * - Polling frequently for active/running items
 * - Backing off exponentially for stable items
 * - Pausing when page is hidden
 * - Resuming on page visibility
 */

import { useEffect, useCallback, useRef, useState } from "react";

interface UsePollOptions {
  /** Base interval in milliseconds (default: 5000) */
  interval?: number;
  /** Maximum interval for exponential backoff (default: 30000) */
  maxInterval?: number;
  /** Whether to enable exponential backoff (default: true) */
  enableBackoff?: boolean;
  /** Function to determine if polling should be frequent (default: always fast) */
  shouldPollFast?: () => boolean;
  /** Whether polling is enabled (default: true) */
  enabled?: boolean;
}

export function usePoll(
  callback: () => Promise<void> | void,
  options: UsePollOptions = {}
) {
  const {
    interval = 5000,
    maxInterval = 30000,
    enableBackoff = true,
    shouldPollFast,
    enabled = true,
  } = options;

  const [currentInterval, setCurrentInterval] = useState(interval);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const consecutiveSuccessesRef = useRef(0);
  const lastPollTimeRef = useRef<number>(Date.now());

  // Clear existing timeout
  const clearPollTimeout = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  // Schedule next poll
  const scheduleNextPoll = useCallback(
    (nextInterval: number) => {
      clearPollTimeout();
      
      if (!enabled) return;

      timeoutRef.current = setTimeout(() => {
        callback();
        lastPollTimeRef.current = Date.now();
      }, nextInterval);
    },
    [callback, clearPollTimeout, enabled]
  );

  // Calculate next interval with exponential backoff
  const getNextInterval = useCallback(() => {
    // If shouldPollFast returns true, always use base interval
    if (shouldPollFast && shouldPollFast()) {
      consecutiveSuccessesRef.current = 0;
      return interval;
    }

    // Exponential backoff based on consecutive successes
    if (enableBackoff) {
      const backoffFactor = Math.min(
        Math.pow(1.5, consecutiveSuccessesRef.current),
        maxInterval / interval
      );
      return Math.min(interval * backoffFactor, maxInterval);
    }

    return interval;
  }, [interval, maxInterval, enableBackoff, shouldPollFast]);

  // Execute callback and schedule next poll
  const poll = useCallback(async () => {
    try {
      await callback();
      
      // Successful poll - increment consecutive successes
      consecutiveSuccessesRef.current += 1;
      
      const nextInterval = getNextInterval();
      setCurrentInterval(nextInterval);
      scheduleNextPoll(nextInterval);
    } catch (error) {
      console.error("[usePoll] Error during poll:", error);
      
      // On error, reset to base interval
      consecutiveSuccessesRef.current = 0;
      setCurrentInterval(interval);
      scheduleNextPoll(interval);
    }
  }, [callback, getNextInterval, scheduleNextPoll, interval]);

  // Handle visibility change
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        console.log("[usePoll] Page visible, resuming polling");
        
        // If we haven't polled in a while, poll immediately
        const timeSinceLastPoll = Date.now() - lastPollTimeRef.current;
        if (timeSinceLastPoll > currentInterval) {
          poll();
        } else {
          // Otherwise, schedule next poll
          scheduleNextPoll(currentInterval - timeSinceLastPoll);
        }
      } else {
        console.log("[usePoll] Page hidden, pausing polling");
        clearPollTimeout();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [poll, scheduleNextPoll, clearPollTimeout, currentInterval]);

  // Start polling on mount
  useEffect(() => {
    if (!enabled) {
      clearPollTimeout();
      return;
    }

    // Initial poll
    poll();

    return () => {
      clearPollTimeout();
    };
  }, [enabled, poll, clearPollTimeout]);

  return {
    /** Current polling interval in ms */
    currentInterval,
    /** Force an immediate poll and reset backoff */
    forcePoll: () => {
      consecutiveSuccessesRef.current = 0;
      setCurrentInterval(interval);
      poll();
    },
  };
}

/**
 * Example usage:
 * 
 * const { currentInterval, forcePoll } = usePoll(
 *   async () => {
 *     const data = await fetchData();
 *     setData(data);
 *   },
 *   {
 *     interval: 5000,
 *     maxInterval: 30000,
 *     shouldPollFast: () => data?.hasActiveItems || false,
 *   }
 * );
 */
