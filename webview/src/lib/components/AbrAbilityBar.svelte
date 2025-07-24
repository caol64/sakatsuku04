<script lang="ts">
	let { value = 0, min = -5, max = 5 } = $props();

	// 防御性处理：避免非法范围
	if (min >= max) {
		throw new Error("Invalid range: min must be less than max.");
	}

	// 计算正负区间宽度占比（用于定位中心线）
	const range = max - min;
	const zeroPosPercent = (-min / range) * 100;

	// 当前值所占百分比
	const valuePercent = ((value - min) / range) * 100;

	// 是否为纯正区间
	const isPositiveOnly = min >= 0;

	// 分离负值与正值宽度（都相对于总宽度）
	let negWidth = $derived.by(() =>
		value < 0 ? `${(Math.abs(value - Math.max(0, min)) / range) * 100}%` : "0%"
	);
	let posWidth = $derived.by(() =>
		value > 0 ? `${(value - Math.max(0, min)) / range * 100}%` : "0%"
	);
</script>

<div class="relative h-3 w-full bg-gray-200 dark:bg-neutral-700 rounded overflow-hidden">
	<!-- 中心线 -->
	<div
		class="absolute inset-y-0 bg-gray-400 z-10"
		style="left: {zeroPosPercent}%; width: 1px"
	></div>

	<!-- 左侧负值 -->
	{#if !isPositiveOnly}
		<div
			class="absolute top-0 bottom-0 bg-red-400 z-0"
			style="left: {zeroPosPercent}%; width: {negWidth}; transform: translateX(-100%)"
		></div>
	{/if}

	<!-- 右侧正值 -->
	{#if value > 0}
		<div
			class="absolute top-0 bottom-0 bg-green-400 z-0"
			style="left: {zeroPosPercent}%; width: {posWidth}"
		></div>
	{/if}
</div>
