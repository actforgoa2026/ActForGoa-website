import './goa-landscape.css';

/** Decorative reuse of the documented footer artwork, never place evidence. */
export default function GoaLandscape({ placement }: { placement: 'horizon' | 'heading' }) {
  return <div className={`goa-landscape goa-landscape--${placement}`} aria-hidden="true">
    <img
      src="/assets/footer/goa-stippled-landscape.webp"
      alt=""
      width={2172}
      height={724}
      loading={placement === 'horizon' ? 'lazy' : 'eager'}
      decoding="async"
    />
  </div>;
}
