/** Equal-distance samples along an inward spiral, so inner turns move faster. */
export function createOrbitPath(radius = 1050, turns = 4, samples = 4096) {
  const points = Array.from({length:samples + 1}, (_, index) => {
    const progress = index / samples;
    const angle = progress * turns * Math.PI * 2;
    const distance = radius * (1 - progress);
    return {x:Math.cos(angle) * distance, y:Math.sin(angle) * distance};
  });
  const lengths = [0];
  for (let i = 1; i < points.length; i++) lengths.push(lengths[i-1] + Math.hypot(points[i].x-points[i-1].x, points[i].y-points[i-1].y));
  const total = lengths[lengths.length-1];
  const equal = Array.from({length:samples + 1}, (_, index) => {
    const target = index / samples * total;
    let low = 0, high = samples;
    while (low < high) {const middle = (low + high) >>> 1; if (lengths[middle] < target) low = middle + 1; else high = middle;}
    const right = Math.max(1, low), left = right - 1;
    const fraction = (target-lengths[left]) / (lengths[right]-lengths[left] || 1);
    return {x:points[left].x+(points[right].x-points[left].x)*fraction,y:points[left].y+(points[right].y-points[left].y)*fraction};
  });
  return {length:total, radius, point(progress:number) {
    const position = ((progress % 1 + 1) % 1) * samples;
    const index = Math.floor(position), fraction = position - index;
    return {x:equal[index].x+(equal[index+1].x-equal[index].x)*fraction,y:equal[index].y+(equal[index+1].y-equal[index].y)*fraction};
  }};
}
/** Gentle version of Cosmos's ramp-up followed by quadratic burst decay. */
export function orbitEntranceSpeed(elapsed:number) {
  const ramp = Math.min(elapsed / 700, 1) ** 2;
  const remaining = 1 - Math.min(elapsed / 3200, 1);
  return 1 + 6.9 * remaining ** 2 * ramp;
}
