import type { Meta, StoryObj } from '@storybook/react';
import Button from './Button';

const meta: Meta<typeof Button> = {
  title: 'Design System/Button',
  component: Button,
};
export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = { args: { children: 'Recommend' } };
export const Ghost: Story = { args: { variant: 'ghost', children: 'Cancel' } };
export const Small: Story = { args: { size: 'sm', children: 'Small' } };
export const Disabled: Story = { args: { disabled: true, children: 'Disabled' } };
