import type { ButtonHTMLAttributes } from 'react';

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'ghost';
  size?: 'sm' | 'md';
};

export default function Button({ variant = 'primary', size = 'md', ...rest }: Props) {
  return <button className={`btn btn--${variant} btn--${size}`} {...rest} />;
}
