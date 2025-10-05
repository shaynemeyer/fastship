export default function NumberLabel({
  value,
  label,
}: {
  value: number;
  label: string;
}) {
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-gray-200 p-4">
      <h1 className="text-4xl font-bold">{value}</h1>
      <p className="text-gray-500">{label}</p>
    </div>
  );
}
