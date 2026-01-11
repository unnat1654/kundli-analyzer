import CreatableSelect from 'react-select/creatable';
import type { MultiValue, ActionMeta } from 'react-select';

// 1. Define the shape of your option
export interface Option {
  value: string;
  label: string;
}

interface CreatableMultiSelectProps {
  value: readonly Option[]; 
  onChange: (val: readonly Option[]) => void;
  placeholder: string;
  defaultOptions: string[];
}

export function CreatableMultiSelect({value, onChange, placeholder, defaultOptions }: CreatableMultiSelectProps) {
  // 2. Explicitly type useState as an array of 'Option'
  const optionList: Option[] = defaultOptions.map(item => ({ 
    value: item, 
    label: item 
  }));

  // 3. Typed Change Handler
  const handleChange = (
    newValue: MultiValue<Option>, 
    _actionMeta: ActionMeta<Option>
  ) => {
    // newValue is 'readonly Option[]', which matches our state type now
    onChange(newValue as readonly Option[]);
  };

  return (
    <CreatableSelect
      isMulti
      isClearable
      options={optionList}
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
    />
  );
}