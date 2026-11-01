import { Link, type LinkProps } from "react-router-dom";

import { buttonClasses, type ButtonSize, type ButtonVariant } from "./Button";

export type LinkButtonProps = LinkProps & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

/** Link com a aparência dos botões, para navegação sem perder a semântica. */
export function LinkButton({
  variant = "primary",
  size = "md",
  className,
  ...props
}: LinkButtonProps) {
  return <Link {...props} className={buttonClasses(variant, size, className)} />;
}
