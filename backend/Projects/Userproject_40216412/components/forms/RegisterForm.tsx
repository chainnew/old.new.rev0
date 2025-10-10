import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { registerSchema, RegisterFormData } from '../../schemas/validationSchemas';
import { FormField } from '../ui/FormField';

export const RegisterForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    // Simulate API call
    console.log('Register data:', data);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    alert('Registration successful!');
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto p-4 bg-white shadow-md rounded">
      <h2 className="text-2xl font-bold mb-4">Register</h2>
      <FormField
        label="Name"
        name="name"
        register={register}
        error={errors.name}
        placeholder="Enter your name"
      />
      <FormField
        label="Email"
        name="email"
        type="email"
        register={register}
        error={errors.email}
        placeholder="Enter your email"
      />
      <FormField
        label="Password"
        name="password"
        type="password"
        register={register}
        error={errors.password}
        placeholder="Enter your password"
      />
      <FormField
        label="Confirm Password"
        name="confirmPassword"
        type="password"
        register={register}
        error={errors.confirmPassword}
        placeholder="Confirm your password"
      />
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
      >
        {isSubmitting ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
};