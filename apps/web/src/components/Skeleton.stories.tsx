import type { Meta, StoryObj } from '@storybook/react';
import Skeleton, { MovieCardSkeleton } from './Skeleton';

const meta: Meta<typeof Skeleton> = {
  title: 'Design System/Skeleton',
  component: Skeleton,
};
export default meta;
type Story = StoryObj<typeof Skeleton>;

export const Default: Story = { args: {} };
export const CardOnly: Story = {
  render: () => <MovieCardSkeleton />,
};
