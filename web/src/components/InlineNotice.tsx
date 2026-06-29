import { X } from "lucide-react";
import { useEffect } from "react";

type InlineNoticeProps = {
  message: string;
  type?: "success" | "error";
  autoHideMs?: number;
  onClose: () => void;
};

export function InlineNotice({
  message,
  type = "success",
  autoHideMs = 6000,
  onClose,
}: InlineNoticeProps) {
  useEffect(() => {
    if (!message || autoHideMs <= 0) return undefined;
    const timer = window.setTimeout(onClose, autoHideMs);
    return () => window.clearTimeout(timer);
  }, [autoHideMs, message, onClose]);

  if (!message) return null;

  const showConfirmAction = type === "error";

  return (
    <div className="notice-backdrop" onMouseDown={onClose} role="presentation">
      <div className={`inline-alert ${type} dismissible`} onMouseDown={(event) => event.stopPropagation()} role="alert">
        <span>{message}</span>
        <div className="notice-actions">
          {showConfirmAction && (
            <button className="notice-ok" onClick={onClose} type="button">
              Tamam
            </button>
          )}
          <button aria-label="Bildirimi kapat" onClick={onClose} type="button">
            <X size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
