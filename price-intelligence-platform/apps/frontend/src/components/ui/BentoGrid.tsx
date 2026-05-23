import { cn } from "../../lib/utils";
import { motion } from "framer-motion";

export const BentoGrid = ({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) => {
  return (
    <div
      className={cn(
        "grid md:auto-rows-[18rem] grid-cols-1 md:grid-cols-3 gap-4",
        className
      )}
    >
      {children}
    </div>
  );
};

export const BentoGridItem = ({
  className,
  title,
  description,
  header,
  icon,
}: {
  className?: string;
  title?: string | React.ReactNode;
  description?: string | React.ReactNode;
  header?: React.ReactNode;
  icon?: React.ReactNode;
}) => {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className={cn(
        "rounded-3xl group/bento transition-all duration-300 overflow-hidden flex flex-col space-y-4 glass-card-hover p-5",
        className
      )}
    >
      {header}
      <div className="transition duration-200">
        <div className="flex items-center gap-2 mb-1">
          {icon}
          <div className="font-bold text-sm text-white">
            {title}
          </div>
        </div>
        <div className="text-xs text-neutral-500 font-medium">
          {description}
        </div>
      </div>
    </motion.div>
  );
};
