<script lang="ts">
    let { abilities = Array(4).fill(0) }: { abilities: number[] } = $props();
    const labels = ["新人", "谈判", "现役", "搜索"];
    const numSides = 4;
    const angleStep = (2 * Math.PI) / numSides;
    const radius = 100;

    function point(factor: number, index: number) {
        const angle = angleStep * index - Math.PI / 2;
        return {
            x: radius * factor * Math.cos(angle),
            y: radius * factor * Math.sin(angle),
        };
    }

    function playerHexagonConvert(input_value: number) {
        let p = input_value + 10;
        let v = p > 90 ? 360 : p * 4;
        return Math.floor(((v + Math.min(p, 90)) * 20) / 90);
    }
</script>

<div class="flex justify-center w-full bg-white dark:bg-gray-700 rounded-lg">
    <svg
        width="240"
        height="240"
        viewBox="-120 -120 240 240"
        class="m-2"
    >
        <!-- 绘制雷达网格 -->
        {#each Array(5) as _, layer}
            <polygon
                fill="none"
                stroke="currentColor"
                stroke-width="0.5"
                points={Array(numSides)
                    .fill(0)
                    .map((_, i) => {
                        const p = point((layer + 1) / 5, i);
                        return `${p.x},${p.y}`;
                    })
                    .join(" ")}
            />
        {/each}

        <!-- 连接各顶点 -->
        {#each Array(numSides) as _, i}
            <line
                x1="0"
                y1="0"
                x2={point(1, i).x}
                y2={point(1, i).y}
                stroke="#808080"
                stroke-width="0.5"
            />

            <!-- 标签文字 -->
            <text
                x={point(1.15, i).x}
                y={point(1.15, i).y}
                text-anchor="middle"
                alignment-baseline="middle"
                class="text-xs fill-gray-700 dark:fill-white"
            >
                {labels[i]}
            </text>
        {/each}

        <!-- 能力区域 3：最终最大值 -->
        <polygon
            fill="rgba(251, 191, 36, 0.6)"
            stroke-width="0"
            points={abilities
                .map((factor, i) => {
                    const value = playerHexagonConvert(factor) / 100;
                    const p = point(value, i);
                    return `${p.x},${p.y}`;
                })
                .join(" ")}
        />
    </svg>
</div>
