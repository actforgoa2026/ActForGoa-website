/** Date-only values stay calendar dates, never UTC instants. */
export function calendarDate(value:string){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(value))return undefined;
  const [year,month,day]=value.split('-').map(Number),date=new Date(year,month-1,day,12);
  return date.getFullYear()===year&&date.getMonth()===month-1&&date.getDate()===day?date:undefined;
}
export function dateValue(value:Date|undefined){return value?`${value.getFullYear()}-${String(value.getMonth()+1).padStart(2,'0')}-${String(value.getDate()).padStart(2,'0')}`:'';}
