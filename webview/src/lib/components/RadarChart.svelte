<script lang="ts">
    export let abilities = [0.8, 0.6, 0.7, 0.9, 0.4, 0.5]; // 六项能力值，0-1
    const labels = ["进攻", "防守", "体能", "身体", "阵型", "战术"];
    const numSides = 6;
    const angleStep = (2 * Math.PI) / numSides;
    const radius = 100;

    function point(factor: number, index: number) {
        const angle = angleStep * index - Math.PI / 2;
        return {
            x: radius * factor * Math.cos(angle),
            y: radius * factor * Math.sin(angle),
        };
    }
</script>

<div class="flex items-center justify-center w-full h-full">
    <svg
        width="240"
        height="240"
        viewBox="-120 -120 240 240"
        class="bg-white rounded"
    >
        <!-- 绘制雷达网格 -->
        {#each Array(5) as _, layer}
            <polygon
                fill="none"
                stroke="#e5e7eb"
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
                stroke="#e5e7eb"
                stroke-width="0.5"
            />

            <!-- 标签文字 -->
            <text
                x={point(1.15, i).x}
                y={point(1.15, i).y}
                text-anchor="middle"
                alignment-baseline="middle"
                class="text-xs fill-gray-700"
            >
                {labels[i]}
            </text>
        {/each}

        <!-- 能力区域 -->
        <polygon
            fill="rgba(59,130,246,0.5)"
            stroke="rgba(37,99,235,1)"
            stroke-width="2"
            points={abilities
                .map((factor, i) => {
                    const p = point(factor, i);
                    return `${p.x},${p.y}`;
                })
                .join(" ")}
        />
    </svg>
</div>
