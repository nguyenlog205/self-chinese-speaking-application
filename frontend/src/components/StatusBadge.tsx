import { useBackendStatus } from "../hooks/useBackendStatus";

export default function StatusBadge() {
  const { status, ping } = useBackendStatus();

  const isOnline = status === "online";

  return (
    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-gray-200 dark:bg-gray-700 text-sm">
      <span
        className={`inline-block w-2 h-2 rounded-full ${
          isOnline ? "bg-green-500" : "bg-red-500"
        }`}
      />
      <span className="font-medium">
        {isOnline ? "Online" : "Offline"}
        {isOnline && ping && (
          <span className="ml-1 text-xs text-gray-500 dark:text-gray-400">
            ({ping}ms)
          </span>
        )}
      </span>
    </div>
  );
}