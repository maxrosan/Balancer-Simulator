
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <time.h>
#include <unistd.h>
#include <stdint.h>

// ./a.out <number of blocks> <number of seconds>

uint32_t mlog2(uint32_t x) {
	uint32_t n = 0;

	x = x >> 1;

	while (x) {
		n++;
		x = x >> 1;
	}

	return n;
}

int main(int argc, char **argv) {

	uint8_t **blocks, *ptA;
	int nblocks = atoi(argv[1]), i, j;
	int block_size = 1024 * 1024; // 1MB
	clock_t start, end;
	double avg_elapsed = 0.;
	int num_random_blocks = 10;
	register uint32_t div_NB, div_BS, iA, iB;
	time_t startT, endT, intervalT = atoi(argv[2]);

	srand(time(NULL));


	if (nblocks > 0) {

		blocks = (uint8_t**) malloc(nblocks * sizeof(uint8_t*));

	
		for (i = 0; i < nblocks; i++) {
			blocks[i] = (uint8_t*) malloc(block_size);

			ptA = blocks[i];

			for (j = 0; j < block_size; j++) {
				*ptA = (uint8_t) (rand() % 256);
				ptA++;
			}
		}

		div_NB = ~((~0) << mlog2(nblocks));
		div_BS = ~((~0) << mlog2(block_size));
	}

	startT = endT = time(NULL);
	while ((endT - startT) <= intervalT) { 

		start = clock();

		if (nblocks > 0) {
			for (i = 0; i < block_size; i++) {
				iA = rand() & div_NB;	
				iB = rand() & div_BS;
				blocks[iA][iB] += rand();
			}
		}

		end = clock();

		avg_elapsed += ((double ) end - start) / CLOCKS_PER_SEC;

		endT = time(NULL);

		//fprintf(stderr, "\r I = %lu ", ni);

	}

	//avg_elapsed *= (1./niterations);

	//fprintf(stderr, "\navg time elapsed = %lf\n", avg_elapsed);

	for (i = 0; i < nblocks; i++) {
		free(blocks[i]);
	}

	if (nblocks > 0) {
		free(blocks);
	}

	return EXIT_SUCCESS;

}
