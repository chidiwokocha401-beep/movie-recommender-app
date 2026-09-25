import type { Meta, StoryObj } from '@storybook/react';
import EmptyState from './EmptyState';

const meta: Meta<typeof EmptyState> = {
  title: 'Design System/EmptyState',
  component: EmptyState,
};
export default meta;
type Story = StoryObj<typeof EmptyState>;

export const NoRecommendations: Story = {
  args: {
    title: 'No recommendations yet',
    message: 'Rate a few movies and check back after the nightly update.',
  },
};
