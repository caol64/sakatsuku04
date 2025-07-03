<script lang="ts">
	let { text, children, className = "" } = $props();

	let visible = $state<boolean>(false);
	let x = $state<number>(0);
	let y = $state<number>(0);

	function handleMousemove(event: MouseEvent) {
		x = event.pageX + 10;
		y = event.pageY + 10;
	}
</script>

<div
	class="relative inline-block {className}"
	onmouseenter={() => (visible = true)}
	onmouseleave={() => (visible = false)}
	onmousemove={handleMousemove}
	onfocus={() => (visible = true)}
	onblur={() => (visible = false)}
	role="application"
>
	{@render children?.()}

	{#if visible}
		<div
			id="tooltip-element"
			role="tooltip"
			style="position: fixed; left: {x}px; top: {y}px;"
			class="w-[100px] z-50 rounded-md bg-gray-800 px-3 py-1.5 text-sm font-medium text-white shadow-lg pointer-events-none"
		>
			{@html text}
		</div>
	{/if}
</div>
