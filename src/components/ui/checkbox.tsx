"use client";

import * as React from 'react';
import * as CheckboxPrimitive from '@radix-ui/react-checkbox';
import {Check} from 'lucide-react';
import './controls.css';

// shadcn/ui Checkbox, retaining Radix's keyboard, form and ARIA behavior.
export const Checkbox = React.forwardRef<React.ElementRef<typeof CheckboxPrimitive.Root>, React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root>>(
 function Checkbox({className, ...props}, ref) {
  return <CheckboxPrimitive.Root ref={ref} className={['ui-checkbox', className].filter(Boolean).join(' ')} {...props}>
   <CheckboxPrimitive.Indicator className="ui-checkbox-indicator"><Check size={16} /></CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>;
 },
);
Checkbox.displayName = CheckboxPrimitive.Root.displayName;
