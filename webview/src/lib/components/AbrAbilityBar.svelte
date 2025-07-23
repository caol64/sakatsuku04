<script lang="ts">
	let { value = 0 } = $props(); // -5 to +5

	const total = 5;

	let negWidth = $derived.by(() =>
		value < 0 ? `${(Math.abs(value) / total) * 50}%` : "0%"
	);
	let posWidth = $derived.by(() =>
		value > 0 ? `${(value / total) * 50}%` : "0%"
	);
</script>

<div class="relative h-3 w-full bg-gray-200 dark:bg-neutral-700 rounded overflow-hidden">
	<!-- 中心线 -->
	<div class="absolute inset-y-0 left-1/2 w-0.5 bg-gray-400 z-10"></div>

	<!-- 左侧负值（从中间向左扩展） -->
	<div
		class="absolute left-1/2 top-0 bottom-0 bg-red-400 z-0"
		style="width: {negWidth}; transform: translateX(-100%)"
	></div>

	<!-- 右侧正值（从中间向右扩展） -->
	<div
		class="absolute left-1/2 top-0 bottom-0 bg-green-400 z-0"
		style="width: {posWidth}"
	></div>
</div>
