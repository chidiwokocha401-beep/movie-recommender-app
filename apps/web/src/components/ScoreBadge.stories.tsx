import type { Meta, StoryObj } from '@storybook/react';
import ScoreBadge from './ScoreBadge';

const meta: Meta<typeof ScoreBadge> = {
  title: 'Design System/ScoreBadge',
  component: ScoreBadge,
};
export default meta;
type Story = StoryObj<typeof ScoreBadge>;

export const High: Story = { args: { score: 4.5 } };
export const Mid: Story = { args: { score: 3.2 } };
export const Low: Story = { args: { score: 1.8 } };
