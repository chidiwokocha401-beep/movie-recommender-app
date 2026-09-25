import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import RatingStars from './RatingStars';

const meta: Meta<typeof RatingStars> = {
  title: 'Design System/RatingStars',
  component: RatingStars,
};
export default meta;
type Story = StoryObj<typeof RatingStars>;

export const Empty: Story = { args: {} };
export const ReadOnly: Story = { args: { value: 4, readOnly: true } };

export function Interactive() {
  const [value, setValue] = useState(3);
  return <RatingStars value={value} onRate={setValue} />;
}
