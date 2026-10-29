"use client";

import {forwardRef,useCallback,useRef,type AnchorHTMLAttributes,type RefObject} from 'react';
import {Link,type LinkProps} from 'react-router-dom';
import {motion,useReducedMotion,type Variants} from 'motion/react';
import {motionTokens} from '../lib/motion-tokens';
import type {ButtonSize,ButtonVariant} from './button';
import styles from './button.module.css';

type NativeEvents='onDrag'|'onDragEnd'|'onDragStart'|'onAnimationStart';
type Appearance={variant?:ButtonVariant;size?:ButtonSize;wrap?:boolean};
export type ButtonLinkProps=Appearance & (
  | (Omit<LinkProps,NativeEvents|'href'> & {href?:never})
  | (Omit<AnchorHTMLAttributes<HTMLAnchorElement>,NativeEvents> & {href:string;to?:never;state?:never})
);
const MotionLink=motion.create(Link);
const pressVariants:Variants={
  pressed:(anchor:RefObject<HTMLAnchorElement|null>)=>{
    const width=anchor.current?.offsetWidth??0;
    return {scale:width>220?.985:width&&width<=48?.96:.97,transition:{duration:motionTokens.duration.instant,ease:[...motionTokens.ease.standard]}};
  },
};

/** The installed Arc Button's visual and press treatment, with real anchor semantics.
 * Router links keep modifier-click, open-in-new-tab, history and navigation state.
 * Native href links preserve mail, phone, downloads and external destinations.
 * Children stay direct so navigation grids can arrange icon and label without a second skin.
 */
export const ButtonLink=forwardRef<HTMLAnchorElement,ButtonLinkProps>(function ButtonLink(
  {variant='primary',size='md',wrap=false,className,children,...props},ref,
){
  const reduceMotion=useReducedMotion()??false;
  const anchorRef=useRef<HTMLAnchorElement|null>(null);
  const setRef=useCallback((node:HTMLAnchorElement|null)=>{
    anchorRef.current=node;
    if(typeof ref==='function')ref(node);else if(ref)ref.current=node;
  },[ref]);
  const shared={
    ref:setRef,
    className:[styles.button,styles[variant],styles[size],wrap&&styles.wrap,className].filter(Boolean).join(' '),
    custom:anchorRef,variants:pressVariants,whileTap:reduceMotion?undefined:'pressed',transition:motionTokens.spring.snappy,
  };
  return 'to' in props && props.to!==undefined
    ? <MotionLink {...props as Omit<LinkProps,NativeEvents>} {...shared}>{children}</MotionLink>
    : <motion.a {...props as Omit<AnchorHTMLAttributes<HTMLAnchorElement>,NativeEvents>} {...shared}>{children}</motion.a>;
});
ButtonLink.displayName='ButtonLink';
export default ButtonLink;
