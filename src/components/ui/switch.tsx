"use client";

import type {ComponentProps} from 'react';
import * as SwitchPrimitive from '@radix-ui/react-switch';
import './controls.css';

// shadcn/ui Switch, with its utility classes mapped to the project's CSS tokens.
export function Switch({className, ...props}: ComponentProps<typeof SwitchPrimitive.Root>) {
 return <SwitchPrimitive.Root data-slot="switch" className={['ui-switch', className].filter(Boolean).join(' ')} {...props}>
  <SwitchPrimitive.Thumb data-slot="switch-thumb" className="ui-switch-thumb" />
 </SwitchPrimitive.Root>;
}
