import * as React from "react"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {{
  size?: "sm" | "default" | "lg"
}}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({{ className = "", size = "default", ...props }}, ref) => {{
    const sizes = {{ sm: "h-9 px-3", default: "h-10 px-4 py-2", lg: "h-11 px-8" }}
    return <button className={{`rounded-md font-medium ${{sizes[size]}} ${{className}}`}} ref={{ref}} {{...props}} />
  }}
)
Button.displayName = "Button"
export {{ Button }}
