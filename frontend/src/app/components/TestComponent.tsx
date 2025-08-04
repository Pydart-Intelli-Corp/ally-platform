'use client';

import React from 'react';
import { Button, Typography, Box } from '@mui/material';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { create } from 'zustand';
import axios from 'axios';

// Zustand store test with proper TypeScript
interface TestState {
  count: number;
  increment: () => void;
  decrement: () => void;
}

const useTestStore = create<TestState>((set) => ({
  count: 0,
  increment: () => set((state: TestState) => ({ count: state.count + 1 })),
  decrement: () => set((state: TestState) => ({ count: state.count - 1 })),
}));

interface FormData {
  testField: string;
}

const TestComponent = () => {
  const { count, increment, decrement } = useTestStore();
  const { register, handleSubmit } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    console.log('Form data:', data);
    try {
      // Test axios (this would normally call your backend)
      const response = await axios.get('https://jsonplaceholder.typicode.com/posts/1');
      console.log('API Response:', response.data);
    } catch (error) {
      console.error('API Error:', error);
    }
  };

  return (
    <Box className="p-8 space-y-6">
      {/* TailwindCSS and Material-UI Test */}
      <Typography variant="h4" className="text-blue-600 font-bold">
        ✅ Frontend Dependencies Test
      </Typography>

      {/* Framer Motion Test */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="p-4 bg-green-100 rounded-lg"
      >
        <Typography variant="h6">Framer Motion Animation ✅</Typography>
      </motion.div>

      {/* Zustand State Management Test */}
      <Box className="p-4 bg-blue-100 rounded-lg">
        <Typography variant="h6" className="mb-4">
          Zustand State: {count} ✅
        </Typography>
        <div className="space-x-2">
          <Button variant="contained" onClick={increment}>
            Increment
          </Button>
          <Button variant="outlined" onClick={decrement}>
            Decrement
          </Button>
        </div>
      </Box>

      {/* React Hook Form Test */}
      <Box className="p-4 bg-yellow-100 rounded-lg">
        <Typography variant="h6" className="mb-4">
          React Hook Form + Axios Test ✅
        </Typography>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <input
            {...register('testField')}
            placeholder="Enter test data"
            className="p-2 border rounded w-full"
          />
          <Button type="submit" variant="contained" color="primary">
            Submit & Test Axios
          </Button>
        </form>
      </Box>

      {/* TailwindCSS Test */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-red-200 rounded-lg">
          <Typography>TailwindCSS Grid ✅</Typography>
        </div>
        <div className="p-4 bg-green-200 rounded-lg">
          <Typography>Responsive Layout ✅</Typography>
        </div>
        <div className="p-4 bg-purple-200 rounded-lg">
          <Typography>Utility Classes ✅</Typography>
        </div>
      </div>

      <Typography variant="body2" className="text-gray-600">
        All frontend dependencies working correctly! 🎉
      </Typography>
    </Box>
  );
};

export default TestComponent;
