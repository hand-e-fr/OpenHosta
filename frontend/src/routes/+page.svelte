<script>
    let board = Array(3).fill("").map(() => Array(3).fill(""));

    async function handleClick(row, col) {
        const response = await fetch('http://127.0.0.1:3000/tic-tac-toe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ row, col }),
        });

        if (!response.ok) {
            console.error('HTTP error', response.status);
            return;
        }

        const updatedBoard = await response.json();
        board = updatedBoard;
    }
</script>

<style>
    .board {
        display: grid;
        grid-template-columns: repeat(3, 0fr);
        gap: 10px;
    }
    button {
        height: 150px;
        width: 150px;
    }
</style>

<div class="board">
    {#each board as row, i}
        {#each row as cell, j}
            <button on:click={() => handleClick(i, j)}>{cell}</button>
        {/each}
    {/each}
</div>