"use client";

import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Wifi, WifiOff, AlertCircle, Loader2 } from 'lucide-react';
import { gameApi, isDevelopmentMode, devGameApi } from '@/lib/api-client';
import type { ConnectionStatus } from '@/types/api';

interface ConnectionStatusDisplayProps {
  className?: string;
  showLabel?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function ConnectionStatusDisplay({
  className = "",
  showLabel = true,
  autoRefresh = true,
  refreshInterval = 30000 // 30 seconds
}: ConnectionStatusDisplayProps) {
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setError(null);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const connectionStatus = await client.getConnectionStatus();
      setStatus(connectionStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch connection status');
      setStatus(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();

    if (autoRefresh) {
      const interval = setInterval(fetchStatus, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  if (loading) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
        {showLabel && <span className="text-sm text-gray-500">Checking connection...</span>}
      </div>
    );
  }

  if (error || !status) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <AlertCircle className="h-4 w-4 text-red-500" />
        {showLabel && (
          <Badge variant="destructive" className="text-xs">
            Connection Error
          </Badge>
        )}
      </div>
    );
  }

  const getStatusColor = () => {
    if (status.connected) return 'text-green-500';
    return 'text-red-500';
  };

  const getStatusIcon = () => {
    if (status.connected) {
      return <Wifi className={`h-4 w-4 ${getStatusColor()}`} />;
    }
    return <WifiOff className={`h-4 w-4 ${getStatusColor()}`} />;
  };

  const getStatusBadge = () => {
    if (status.connected) {
      return (
        <Badge variant="outline" className="text-xs border-green-500 text-green-700 bg-green-50">
          {status.provider.toUpperCase()} Connected
        </Badge>
      );
    }
    return (
      <Badge variant="destructive" className="text-xs">
        {status.provider.toUpperCase()} Disconnected
      </Badge>
    );
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {getStatusIcon()}
      {showLabel && (
        <>
          {getStatusBadge()}
          <span className="text-xs text-gray-500">
            {status.model}
          </span>
        </>
      )}
    </div>
  );
}

// Compact version for headers/navbars
export function ConnectionStatusCompact({ className = "" }: { className?: string }) {
  return (
    <ConnectionStatusDisplay
      className={className}
      showLabel={false}
      autoRefresh={true}
      refreshInterval={60000} // 1 minute for compact version
    />
  );
}

// Detailed version with refresh button
export function ConnectionStatusDetailed({ className = "" }: { className?: string }) {
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStatus = async (showRefreshing = false) => {
    try {
      if (showRefreshing) setRefreshing(true);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const connectionStatus = await client.getConnectionStatus();
      setStatus(connectionStatus);
    } catch (err) {
      console.error('Failed to fetch connection status:', err);
    } finally {
      setLoading(false);
      if (showRefreshing) setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleRefresh = () => {
    fetchStatus(true);
  };

  if (loading) {
    return (
      <div className={`p-4 border rounded-lg bg-white ${className}`}>
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
          <span className="text-sm text-gray-500">Checking AI connection...</span>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className={`p-4 border rounded-lg bg-red-50 border-red-200 ${className}`}>
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-700">Failed to check connection status</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-4 border rounded-lg ${status.connected ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
      } ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {status.connected ? (
            <Wifi className="h-5 w-5 text-green-500" />
          ) : (
            <WifiOff className="h-5 w-5 text-red-500" />
          )}

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-sm">
                {status.provider.toUpperCase()} AI Provider
              </span>
              <Badge
                variant={status.connected ? "outline" : "destructive"}
                className={status.connected ? "border-green-500 text-green-700" : ""}
              >
                {status.connected ? 'Connected' : 'Disconnected'}
              </Badge>
            </div>

            <div className="text-xs text-gray-600 space-y-1">
              <div>Model: {status.model}</div>
              <div>Endpoint: {status.base_url}</div>
              {status.error && (
                <div className="text-red-600">Error: {status.error}</div>
              )}
              <div>Last checked: {new Date(status.timestamp).toLocaleTimeString()}</div>
            </div>
          </div>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
          title="Refresh connection status"
        >
          <Loader2 className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>
    </div>
  );
}