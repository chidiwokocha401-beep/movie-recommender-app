import type { Meta, StoryObj } from '@storybook/react';
import Input from './Input';

const meta: Meta<typeof Input> = {
  title: 'Design System/Input',
  component: Input,
};
export default meta;
type Story = StoryObj<typeof Input>;

export const Search: Story = {
  args: { label: 'Search movies', placeholder: 'Star Wars…', type: 'search' },
};
export const WithValue: Story = {
  args: { label: 'Search movies', defaultValue: 'Fargo' },
};
