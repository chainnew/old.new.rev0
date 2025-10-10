import { User } from '../types/user';

let users: User[] = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    createdAt: new Date('2023-01-01'),
  },
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane@example.com',
    createdAt: new Date('2023-02-01'),
  },
];

let nextId = 3;

export const getAllUsers = (): User[] => users;

export const getUserById = (id: string): User | undefined => users.find(u => u.id === id);

export const createUser = (name: string, email: string): User => {
  const newUser: User = {
    id: nextId.toString(),
    name,
    email,
    createdAt: new Date(),
  };
  users.push(newUser);
  nextId++;
  return newUser;
};

export const updateUser = (id: string, name: string, email: string): User | null => {
  const userIndex = users.findIndex(u => u.id === id);
  if (userIndex === -1) return null;
  users[userIndex] = { ...users[userIndex], name, email };
  return users[userIndex];
};

export const deleteUser = (id: string): boolean => {
  const userIndex = users.findIndex(u => u.id === id);
  if (userIndex === -1) return false;
  users.splice(userIndex, 1);
  return true;
};