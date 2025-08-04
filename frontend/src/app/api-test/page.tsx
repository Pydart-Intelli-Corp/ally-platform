'use client';

import React, { useState } from 'react';
import { Button, Typography, Box, Alert } from '@mui/material';
import axios from 'axios';

interface ApiResponse {
  message?: string;
  timestamp?: string;
  dependencies_status?: Record<string, string>;
}

export default function ApiTestPage() {
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testBackendConnection = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await axios.get('/api/test');
      setResponse(result.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const testDependencies = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await axios.get('/api/test-dependencies');
      setResponse(result.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box className="p-8 space-y-6">
      <Typography variant="h4" className="text-blue-600 font-bold">
        API Test Page
      </Typography>
      
      <Box className="space-y-4">
        <Button 
          variant="contained" 
          onClick={testBackendConnection}
          disabled={loading}
          className="mr-4"
        >
          {loading ? 'Testing...' : 'Test Backend Connection'}
        </Button>
        
        <Button 
          variant="outlined" 
          onClick={testDependencies}
          disabled={loading}
        >
          {loading ? 'Testing...' : 'Test Dependencies'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error">
          Error: {error}
        </Alert>
      )}

      {response && (
        <Box className="mt-6 p-4 bg-gray-100 rounded">
          <Typography variant="h6">Response:</Typography>
          <pre className="mt-2 text-sm overflow-x-auto">
            {JSON.stringify(response, null, 2)}
          </pre>
        </Box>
      )}
    </Box>
  );
}