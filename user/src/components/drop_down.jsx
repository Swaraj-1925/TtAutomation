import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/react'
import { ChevronDownIcon } from '@heroicons/react/20/solid'

export default function Dropdown({ title, options, selectedOption, onSelect }) {
    const handleSelect = (option) => {
        // Prevent any default behavior
        onSelect(option);
    }
    return (

        <Menu as="div" className="relative inline-block text-left">
            <div>
                <MenuButton className="inline-flex w-full justify-center gap-x-1.5 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 ring-1 shadow-xs ring-gray-300 ring-inset hover:bg-gray-50">
                    {selectedOption || title}
                    <ChevronDownIcon aria-hidden="true" className="-mr-1 size-5 text-gray-400" />
                </MenuButton>
            </div>

            <MenuItems
                transition
                className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white ring-1 shadow-lg ring-black/5 transition focus:outline-hidden data-closed:scale-95 data-closed:transform data-closed:opacity-0 data-enter:duration-100 data-enter:ease-out data-leave:duration-75 data-leave:ease-in"
            >
                <div className="py-1">
                    {options.map((option, index) => (
                        <MenuItem key={index}>
                            {({ active }) => (
                                <button
                                    onClick={(e) => {
                                        e.preventDefault(); // Prevent any default action
                                        handleSelect(option);
                                    }}
                                    className={`${
                                        active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                                    } block w-full px-4 py-2 text-sm text-left`}
                                >
                                    {option}
                                </button>
                            )}
                        </MenuItem>
                    ))}

                </div>
            </MenuItems>
        </Menu>
    )
}
