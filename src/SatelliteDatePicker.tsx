import {InlineDatePicker as DatePicker} from './components/arc/date-picker/inline-date-picker';
import {calendarDate,dateValue} from './satellite-dates';

export function SatelliteDatePicker({label,value,onChange,min,max,disabled=false,alignEnd=false}:{label:string;value:string;onChange:(value:string)=>void;min?:string;max?:string;disabled?:boolean;alignEnd?:boolean}){
  return <DatePicker label={label} value={calendarDate(value)} onChange={date=>onChange(dateValue(date))} minDate={min?calendarDate(min):undefined} maxDate={max?calendarDate(max):undefined} locale="en-IN" format={{day:'numeric',month:'short',year:'numeric'}} showToday disabled={disabled} className={'satellite-date-picker'+(alignEnd?' satellite-date-end':'')}/>;
}
