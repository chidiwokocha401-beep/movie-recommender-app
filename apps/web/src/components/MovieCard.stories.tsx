import type { Meta, StoryObj } from '@storybook/react';
import MovieCard from './MovieCard';

const meta: Meta<typeof MovieCard> = {
  title: 'Design System/MovieCard',
  component: MovieCard,
};
export default meta;
type Story = StoryObj<typeof MovieCard>;

export const Basic: Story = {
  args: { title: 'Casablanca (1942)', subtitle: 'Drama · Romance' },
};
export const WithScore: Story = {
  args: { title: 'Casablanca (1942)', subtitle: 'Drama · Romance', score: 4.5 },
};
