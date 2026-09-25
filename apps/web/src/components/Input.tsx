import type { InputHTMLAttributes } from 'react';
import { useId } from 'react';

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
};

export default function Input({ label, id, ...rest }: Props) {
  const autoId = useId();
  const inputId = id ?? autoId;
  return (
    <div>
      <label className="input__label" htmlFor={inputId}>
        {label}
      </label>
      <input className="input" id={inputId} {...rest} />
    </div>
  );
}
