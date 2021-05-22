public class DigNumAnalysis
{
	/**
	 *   Seven segment digital number display:
	 *   --- 0 ---
	 *   |       |
	 *   1       2
	 *   |       |
	 *   --- 3 ---
	 *   |       |
	 *   4       5
	 *   |       |
	 *   --- 6 ---
	 *   each number refers to the bit (e.g. 0 -> 2^0) in question
	 */
	static int Nums[][] = {
		{
		/* 0 */ 1 + 2 + 4 + 0 + 16 + 32 + 64,
		/* 1 */ 0 + 0 + 4 + 0 +  0 + 32 +  0,
		/* 2 */ 1 + 0 + 4 + 8 + 16 +  0 + 64,
		/* 3 */ 1 + 0 + 4 + 8 +  0 + 32 + 64,
		/* 4 */ 0 + 2 + 4 + 8 +  0 + 32 +  0,
		/* 5 */ 1 + 2 + 0 + 8 +  0 + 32 + 64,
		/* 6 */ 1 + 2 + 0 + 8 + 16 + 32 + 64,
		/* 7 */ 1 + 0 + 4 + 0 +  0 + 32 +  0,
		/* 8 */ 1 + 2 + 4 + 8 + 16 + 32 + 64,
		/* 9 */ 1 + 2 + 4 + 8 +  0 + 32 +  0,
//		/* A */ 1 + 2 + 4 + 8 + 16 + 32 +  0,
//		/* b */ 0 + 2 + 0 + 8 + 16 + 32 + 64,
//		/* C */ 1 + 2 + 0 + 0 + 16 +  0 + 64,
//		/* d */ 0 + 0 + 4 + 8 + 16 + 32 + 64,
//		/* E */ 1 + 2 + 0 + 8 + 16 +  0 + 64,
//		/* F */ 1 + 2 + 0 + 8 + 16 +  0 +  0,
		},
		{
		/* Alternate 0 */ 0 + 0 + 0 + 8 + 16 + 32 + 64,
		/* Alternate 1 */ 0 + 2 + 0 + 0 + 16 +  0 +  0,
		0,
		0,
		0,
		0,
		/* Alternate 6 */ 0 + 2 + 0 + 8 + 16 + 32 + 64,
		/* Alternate 7 */ 1 + 2 + 4 + 0 +  0 + 32 +  0,
		0,
		/* Alternate 9 */ 1 + 2 + 4 + 8 +  0 + 32 +  0,
//		0,
//		0,
//		0,
//		0,
//		0,
//		0,
		}
	};

	static boolean isUnique(int digits[])
	{
		int i, j;

		for (i = 0; i < digits.length; i++)
		{
			for (j = i + 1; j < digits.length; j++)
			{
				if (digits[i] == digits[j])
					return false;
			}
		}
		return true;
	}

	static boolean isBit(int i, int bit)
	{
		return (0 != (i & (1 << bit)));
	}

	static int numBits(int i)
	{
		int j, c;

		c = 0;
		for (j = 0; j < 8; j++)
		{
			if (isBit(i, j))
			{
				c++;
			}
		}
		return c;
	}

	public static void main(String args[])
	{
		int a0, a1, a6, a7, a9, i, j, best, NumDigits, mask[], digits[];
		boolean goodfilter[];
		String s, sBest;

		NumDigits = Nums[0].length;
		mask = new int[NumDigits];
		// Set up default bits to mask
		for (j = 0; j < NumDigits; j++)
		{
			mask[j] = Nums[0][j];
		}
		digits = new int[NumDigits];
		goodfilter = new boolean[128];
		best = 8;
		sBest = "none";
		for (i = 0; i < 128; i++)
		{
			goodfilter[i] = false;
			for (a0 = 0; 1 >= a0; a0++)
			for (a1 = 0; 1 >= a1; a1++)
			for (a6 = 0; 1 >= a6; a6++)
			for (a7 = 0; 1 >= a7; a7++)
			for (a9 = 0; 1 >= a9; a9++)
			{
				// Populate bits to mask
				mask[0] = Nums[a0][0];
				mask[1] = Nums[a1][1];
				mask[6] = Nums[a6][6];
				mask[7] = Nums[a7][7];
				mask[9] = Nums[a9][9];
				// Apply the 7 bit mask (i)
				for (j = 0; j < NumDigits; j++)
				{
					digits[j] = mask[j] & i;
				}
				// Check if the bits for the digits are unique
				if (isUnique(digits))
				{
					goodfilter[i] = true;
					j = numBits(i);
					s = "Filter works: " + i + " (#bits " + j + ") on "+a0+":"+a1+":"+a6+":"+a7+":"+a9;
					if (j < best)
					{
						sBest = s;
						best = j;
					}
					System.out.println(s);
				}
			}

		}
		System.out.println("BEST = " + sBest);
	}
}

