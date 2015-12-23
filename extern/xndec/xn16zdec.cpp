typedef int XnStatus;
typedef int XnBool;
typedef unsigned char XnUInt8;
typedef signed char XnInt8;
typedef unsigned int XnUInt32;
typedef unsigned short XnUInt16;
typedef signed short XnInt16;
#define NULL 0
#define TRUE 1
#define FALSE 1
#define XN_MAX_UINT16 65536
#define XN_VALIDATE_INPUT_PTR(x)
#define xnLogError(a,b)
#define XN_STATUS_BAD_PARAM -1
#define XN_STATUS_OK 0
#define XN_STATUS_OUTPUT_BUFFER_OVERFLOW -2
#define XN_PREPARE_VAR16_IN_BUFFER(var) (var)
#define xnOSMemSet(a,b,c) memset(a,b,c)
#include <memory.h>
#define abs(x) ((x) < 0 ? -x : x)
// XN_PREPARE_VAR16_IN_BUFFER
// XN_CHECK_OUTPUT_OVERFLOW
/** Returns an input overflow error if x is beyond y */
#define XN_CHECK_OUTPUT_OVERFLOW(x, y)					\
		if (x > y)										\
		{												\
			return (XN_STATUS_OUTPUT_BUFFER_OVERFLOW);	\
		}

#ifdef __MINGW32__
#define DE __declspec(dllexport)
#else
#define DE
#endif
extern "C"
{
	void DE initlibxndec() 
	{}
	XnStatus DE XnStreamUncompressConf4(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize)
{
	// Local function variables
	const XnUInt8* pInputEnd = pInput + nInputSize;
	const XnUInt8* pOutputEnd = 0;
	const XnUInt8* pOrigOutput = pOutput;
	XnUInt8 nValue1;
	XnUInt8 nValue2;

	// Validate the input/output pointers (to make sure none of them is NULL)
	XN_VALIDATE_INPUT_PTR(pInput);
	XN_VALIDATE_INPUT_PTR(pOutput);
	XN_VALIDATE_INPUT_PTR(pnOutputSize);

	if (nInputSize < sizeof(XnUInt8))
	{
		xnLogError(XN_MASK_STREAM_COMPRESSION, "Input size too small");
		return (XN_STATUS_BAD_PARAM);
	}

	if (nInputSize % 2 != 0)
	{
		xnLogError(XN_MASK_STREAM_COMPRESSION, "Input size not word-aligned");
		return (XN_STATUS_BAD_PARAM);
	}

	pOutputEnd = pOutput + *pnOutputSize;

	XN_CHECK_OUTPUT_OVERFLOW(pOutput + (nInputSize * 2), pOutputEnd);

	while (pInput != pInputEnd)
	{
		nValue1 = pInput[0];
		nValue2 = pInput[1];

		pOutput[0] = nValue1 >> 4;
		pOutput[1] = nValue1 & 0xF;
		pOutput[2] = nValue2 >> 4;
		pOutput[3] = nValue2 & 0xF;

		pOutput+=4;
		pInput+=2;
	}

	*pnOutputSize = (XnUInt32)(pOutput - pOrigOutput);

	// All is good...
	return (XN_STATUS_OK);
}

	XnStatus DE XnStreamUncompressImage8Z(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize)
{
	const XnUInt8* pInputEnd = pInput + nInputSize;
	const XnUInt8* pOrigOutput = pOutput;
	XnUInt8 nLastFullValue = 0;
	XnUInt8 cInput = 0;
	XnUInt8 cZeroCounter = 0;
	XnInt8 cInData1 = 0;
	XnInt8 cInData2 = 0;

	// Note: this function does not make sure it stay within the output memory boundaries!

	// Validate the input/output pointers (to make sure none of them is NULL)
	XN_VALIDATE_INPUT_PTR(pInput);
	XN_VALIDATE_INPUT_PTR(pOutput);
	XN_VALIDATE_INPUT_PTR(pnOutputSize);

	if (nInputSize < sizeof(XnUInt8))
	{
		xnLogError(XN_MASK_STREAM_COMPRESSION, "Input size too small");
		return (XN_STATUS_BAD_PARAM);
	}

	// Decode the data...
	nLastFullValue = *pInput;
	*pOutput = nLastFullValue;
	pInput++;
	pOutput++;

	while (pInput != pInputEnd)
	{
		cInput = *pInput;

		if (cInput < 0xE0)
		{		
			cInData1 = cInput >> 4;
			cInData2 = (cInput & 0x0f);		

			nLastFullValue -= (cInData1 - 6);
			*pOutput = nLastFullValue;
			pOutput++;

			if (cInData2 != 0x0f) 
			{
				if (cInData2 != 0x0d)
				{
					nLastFullValue -= (cInData2 - 6);
					*pOutput = nLastFullValue;
					pOutput++;
				}
			}
			else
			{
				pInput++;
				nLastFullValue = *pInput;
				*pOutput = nLastFullValue;
				pOutput++;
			}

			pInput++;
		}
		else if (cInput >= 0xF0)
		{
			cInData1 = cInput << 4;		

			pInput++;
			cInput = *pInput;

			nLastFullValue = cInData1 + (cInput >> 4);	

			*pOutput = nLastFullValue;
			pOutput++;

			cInData2 = cInput & 0xF;

			if (cInData2 == 0x0F) 
			{
				pInput++;
				nLastFullValue = *pInput;
				*pOutput = nLastFullValue;
				pOutput++;
				pInput++;
			}
			else
			{
				if (cInData2 != 0x0D)
				{
					nLastFullValue -= (cInData2 - 6);
					*pOutput = nLastFullValue;
					pOutput++;
				}

				pInput++;
			}
		}
		else //It must be 0xE?
		{
			cZeroCounter = cInput - 0xE0;

			while (cZeroCounter != 0)
			{
				*pOutput = nLastFullValue;						
				pOutput++;

				*pOutput = nLastFullValue;						
				pOutput++;

				cZeroCounter--;
			}

			pInput++;
		}			
	}

	*pnOutputSize = (XnUInt32)(pOutput - pOrigOutput);

	// All is good...
	return (XN_STATUS_OK);
}


XnStatus DE XnStreamUncompressDepth16Z(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt16* pOutput, XnUInt32* pnOutputSize)
{
	// Local function variables
	const XnUInt8* pInputEnd = pInput + nInputSize;
	XnUInt16* pOutputEnd = 0;
	const XnUInt16* pOrigOutput = pOutput;
	XnUInt16 nLastFullValue = 0;
	XnUInt8 cInput = 0;
	XnUInt8 cZeroCounter = 0;
	XnInt8 cInData1 = 0;
	XnInt8 cInData2 = 0;
	XnUInt8 cInData3 = 0;

	// Validate the input/output pointers (to make sure none of them is NULL)
	XN_VALIDATE_INPUT_PTR(pInput);
	XN_VALIDATE_INPUT_PTR(pOutput);
	XN_VALIDATE_INPUT_PTR(pnOutputSize);

	if (nInputSize < sizeof(XnUInt16))
	{
		xnLogError(XN_MASK_STREAM_COMPRESSION, "Input size too small");
		return (XN_STATUS_BAD_PARAM);
	}

	pOutputEnd = pOutput + (*pnOutputSize / sizeof(XnUInt16));

	// Decode the data...
	nLastFullValue = *(XnUInt16*)pInput;
	*pOutput = nLastFullValue;
	pInput+=2;
	pOutput++;

	while (pInput != pInputEnd)
	{
		cInput = *pInput;

		if (cInput < 0xE0)
		{		
			cInData1 = cInput >> 4;
			cInData2 = (cInput & 0x0f);		

			nLastFullValue -= (cInData1 - 6);
			XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
			*pOutput = nLastFullValue;
			pOutput++;

			if (cInData2 != 0x0f) 
			{
				if (cInData2 != 0x0d)
				{
					nLastFullValue -= (cInData2 - 6);
					XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
					*pOutput = nLastFullValue;
					pOutput++;
				}

				pInput++;
			}
			else
			{
				pInput++;

				cInData3 = *pInput;
				if (cInData3 & 0x80)
				{
					nLastFullValue -= (cInData3 - 192);

					XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
					*pOutput = nLastFullValue;

					pOutput++;
					pInput++;
				}
				else
				{
					nLastFullValue = cInData3 << 8;
					pInput++;
					nLastFullValue += *pInput;

					XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
					*pOutput = nLastFullValue;

					pOutput++;
					pInput++;
				}
			}
		}
		else if (cInput == 0xFF)
		{
			pInput++;

			cInData3 = *pInput;

			if (cInData3 & 0x80)
			{
				nLastFullValue -= (cInData3 - 192);

				XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
				*pOutput = nLastFullValue;

				pInput++;
				pOutput++;
			}
			else
			{
				nLastFullValue = cInData3 << 8;
				pInput++;
				nLastFullValue += *pInput;

				XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
				*pOutput = nLastFullValue;

				pInput++;
				pOutput++;
			}
		}
		else //It must be 0xE?
		{
			cZeroCounter = cInput - 0xE0;

			while (cZeroCounter != 0)
			{
				XN_CHECK_OUTPUT_OVERFLOW(pOutput+1, pOutputEnd);
				*pOutput = nLastFullValue;						
				pOutput++;

				*pOutput = nLastFullValue;						
				pOutput++;

				cZeroCounter--;
			}

			pInput++;
		}			
	}

	*pnOutputSize = (XnUInt32)((pOutput - pOrigOutput) * sizeof(XnUInt16));

	// All is good...
	return (XN_STATUS_OK);
}

XnStatus DE XnStreamUncompressDepth16ZWithEmbTable(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt16* pOutput, XnUInt32* pnOutputSize)
{
	// Local function variables
	const XnUInt8* pInputEnd = pInput + nInputSize;
	XnUInt16* pOutputEnd = 0;
	XnUInt16* pOrigOutput = pOutput;
	XnUInt16 nLastFullValue = 0;
	XnUInt8 cInput = 0;
	XnUInt8 cZeroCounter = 0;
	XnInt8 cInData1 = 0;
	XnInt8 cInData2 = 0;
	XnUInt8 cInData3 = 0;
	XnUInt16* pEmbTable = NULL;
	XnUInt16 nEmbTableIdx = 0;

	// Validate the input/output pointers (to make sure none of them is NULL)
	XN_VALIDATE_INPUT_PTR(pInput);
	XN_VALIDATE_INPUT_PTR(pOutput);
	XN_VALIDATE_INPUT_PTR(pnOutputSize);

	if (nInputSize < sizeof(XnUInt16))
	{
		xnLogError(XN_MASK_STREAM_COMPRESSION, "Input size too small");
		return (XN_STATUS_BAD_PARAM);
	}

	nEmbTableIdx = XN_PREPARE_VAR16_IN_BUFFER(*(XnUInt16*)pInput);
	pInput+=2;
	pEmbTable = (XnUInt16*)pInput;
	pInput+=nEmbTableIdx * 2;
	for (XnUInt32 i = 0; i < nEmbTableIdx; i++)
		pEmbTable[i] = XN_PREPARE_VAR16_IN_BUFFER(pEmbTable[i]);

	pOutputEnd = pOutput + (*pnOutputSize / sizeof(XnUInt16));

	// Decode the data...
	nLastFullValue = XN_PREPARE_VAR16_IN_BUFFER(*(XnUInt16*)pInput);
	*pOutput = pEmbTable[nLastFullValue];
	pInput+=2;
	pOutput++;

	while (pInput != pInputEnd)
	{
		cInput = *pInput;

		if (cInput < 0xE0)
		{		
			cInData1 = cInput >> 4;
			cInData2 = (cInput & 0x0f);		

			nLastFullValue -= (cInData1 - 6);
			XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
			*pOutput =  pEmbTable[nLastFullValue];
			pOutput++;

			if (cInData2 != 0x0f) 
			{
				if (cInData2 != 0x0d)
				{
					nLastFullValue -= (cInData2 - 6);
					XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
					*pOutput =  pEmbTable[nLastFullValue];
					pOutput++;
				}

				pInput++;
			}
			else
			{
				pInput++;

				cInData3 = *pInput;
				if (cInData3 & 0x80)
				{
					nLastFullValue -= (cInData3 - 192);

					XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
					*pOutput =  pEmbTable[nLastFullValue];

					pOutput++;
					pInput++;
				}
				else
				{
					nLastFullValue = cInData3 << 8;
					pInput++;
					nLastFullValue += *pInput;

					XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
					*pOutput =  pEmbTable[nLastFullValue];

					pOutput++;
					pInput++;
				}
			}
		}
		else if (cInput == 0xFF)
		{
			pInput++;

			cInData3 = *pInput;

			if (cInData3 & 0x80)
			{
				nLastFullValue -= (cInData3 - 192);

				XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
				*pOutput =  pEmbTable[nLastFullValue];

				pInput++;
				pOutput++;
			}
			else
			{
				nLastFullValue = cInData3 << 8;
				pInput++;
				nLastFullValue += *pInput;

				XN_CHECK_OUTPUT_OVERFLOW(pOutput, pOutputEnd);
				*pOutput =  pEmbTable[nLastFullValue];

				pInput++;
				pOutput++;
			}
		}
		else //It must be 0xE?
		{
			cZeroCounter = cInput - 0xE0;

			while (cZeroCounter != 0)
			{
				XN_CHECK_OUTPUT_OVERFLOW(pOutput+1, pOutputEnd);
				*pOutput =  pEmbTable[nLastFullValue];
				pOutput++;

				*pOutput =  pEmbTable[nLastFullValue];
				pOutput++;

				cZeroCounter--;
			}

			pInput++;
		}			
	}

	*pnOutputSize = (XnUInt32)((pOutput - pOrigOutput) * sizeof(XnUInt16));

	// All is good...
	return (XN_STATUS_OK);
}

XnStatus DE XnStreamCompressDepth16Z(const XnUInt16* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize)
{
	// Local function variables
	const XnUInt16* pInputEnd = pInput + (nInputSize / sizeof(XnUInt16));
	XnUInt8* pOrigOutput = pOutput;
	XnUInt16 nCurrValue = 0;
	XnUInt16 nLastValue = 0;
	XnUInt16 nAbsDiffValue = 0;
	XnInt16 nDiffValue = 0;
	XnUInt8 cOutStage = 0;
	XnUInt8 cOutChar = 0;
	XnUInt8 cZeroCounter = 0;

	// Note: this function does not make sure it stay within the output memory boundaries!

	// Validate the input/output pointers (to make sure none of them is NULL)
	XN_VALIDATE_INPUT_PTR(pInput);
	XN_VALIDATE_INPUT_PTR(pOutput);
	XN_VALIDATE_INPUT_PTR(pnOutputSize);

	if (nInputSize == 0)
	{
		*pnOutputSize = 0;
		return XN_STATUS_OK;
	}

	// Encode the data...
	nLastValue = *pInput;
	*(XnUInt16*)pOutput = nLastValue;
	pInput++;
	pOutput+=2;

	while (pInput != pInputEnd)
	{	
		nCurrValue = *pInput;

		nDiffValue = (nLastValue - nCurrValue);
		nAbsDiffValue = (XnUInt16)abs(nDiffValue);

		if (nAbsDiffValue <= 6)
		{
			nDiffValue += 6;

			if (cOutStage == 0)
			{
				cOutChar = (XnUInt8)(nDiffValue << 4);

				cOutStage = 1;
			}
			else
			{
				cOutChar += (XnUInt8)nDiffValue;

				if (cOutChar == 0x66)
				{
					cZeroCounter++;

					if (cZeroCounter == 15)
					{
						*pOutput = 0xEF;
						pOutput++;

						cZeroCounter = 0;
					}
				}
				else
				{
					if (cZeroCounter != 0)
					{
						*pOutput = 0xE0 + cZeroCounter;
						pOutput++;

						cZeroCounter = 0;
					}

					*pOutput = cOutChar;
					pOutput++;
				}

				cOutStage = 0;
			}
		}
		else
		{
			if (cZeroCounter != 0)
			{
				*pOutput = 0xE0 + cZeroCounter;
				pOutput++;

				cZeroCounter = 0;				
			}

			if (cOutStage == 0)
			{
				cOutChar = 0xFF;				
			}
			else
			{
				cOutChar += 0x0F;
				cOutStage = 0;
			}

			*pOutput = cOutChar;
			pOutput++;		

			if (nAbsDiffValue <= 63)
			{
				nDiffValue += 192;

				*pOutput = (XnUInt8)nDiffValue;
				pOutput++;
			}
			else
			{
				*(XnUInt16*)pOutput = (nCurrValue << 8) + (nCurrValue >> 8);
				pOutput+=2;
			}
		}

		nLastValue = nCurrValue;
		pInput++;
	}

	if (cOutStage != 0)
	{
		*pOutput = cOutChar + 0x0D;
		pOutput++;
	}

	if (cZeroCounter != 0)
	{
		*pOutput = 0xE0 + cZeroCounter;
		pOutput++;
	}

	*pnOutputSize = (XnUInt32)(pOutput - pOrigOutput);

	// All is good...
	return (XN_STATUS_OK);
}

XnStatus DE XnStreamCompressDepth16ZWithEmbTable(const XnUInt16* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize, XnUInt16 nMaxValue)
{
	// Local function variables
	const XnUInt16* pInputEnd = pInput + (nInputSize / sizeof(XnUInt16));
	const XnUInt16* pOrigInput = pInput;
	const XnUInt8* pOrigOutput = pOutput;
	XnUInt16 nCurrValue = 0;
	XnUInt16 nLastValue = 0;
	XnUInt16 nAbsDiffValue = 0;
	XnInt16 nDiffValue = 0;
	XnUInt8 cOutStage = 0;
	XnUInt8 cOutChar = 0;
	XnUInt8 cZeroCounter = 0;
	static XnUInt16 nEmbTable[XN_MAX_UINT16];
	XnUInt16 nEmbTableIdx=0;

	// Note: this function does not make sure it stay within the output memory boundaries!

	// Validate the input/output pointers (to make sure none of them is NULL)
	XN_VALIDATE_INPUT_PTR(pInput);
	XN_VALIDATE_INPUT_PTR(pOutput);
	XN_VALIDATE_INPUT_PTR(pnOutputSize);

	// Create the embedded value translation table...
	pOutput+=2;
	xnOSMemSet(&nEmbTable[0], 0, nMaxValue*sizeof(XnUInt16));

	while (pInput != pInputEnd)
	{
		nEmbTable[*pInput] = 1;
		pInput++;
	}

	for (XnUInt32 i=0; i<nMaxValue; i++)
	{
		if (nEmbTable[i] == 1)
		{
			nEmbTable[i] = nEmbTableIdx;
			nEmbTableIdx++;
			*(XnUInt16*)pOutput = XN_PREPARE_VAR16_IN_BUFFER(XnUInt16(i));
			pOutput+=2;
		}
	}

	*(XnUInt16*)(pOrigOutput) = XN_PREPARE_VAR16_IN_BUFFER(nEmbTableIdx);

	// Encode the data...
	pInput = pOrigInput;
	nLastValue = nEmbTable[*pInput];
	*(XnUInt16*)pOutput = XN_PREPARE_VAR16_IN_BUFFER(nLastValue);
	pInput++;
	pOutput+=2;

// 	for (XnUInt32 i = 0; i < nEmbTableIdx; i++)
// 		nEmbTable[i] = XN_PREPARE_VAR16_IN_BUFFER(nEmbTable[i]);


	while (pInput < pInputEnd)
	{	
		nCurrValue = nEmbTable[*pInput];

		nDiffValue = (nLastValue - nCurrValue);
		nAbsDiffValue = (XnUInt16)abs(nDiffValue);

		if (nAbsDiffValue <= 6)
		{
			nDiffValue += 6;

			if (cOutStage == 0)
			{
				cOutChar = (XnUInt8)(nDiffValue << 4);

				cOutStage = 1;
			}
			else
			{
				cOutChar += (XnUInt8)nDiffValue;

				if (cOutChar == 0x66)
				{
					cZeroCounter++;

					if (cZeroCounter == 15)
					{
						*pOutput = 0xEF;
						pOutput++;

						cZeroCounter = 0;
					}
				}
				else
				{
					if (cZeroCounter != 0)
					{
						*pOutput = 0xE0 + cZeroCounter;
						pOutput++;

						cZeroCounter = 0;
					}

					*pOutput = cOutChar;
					pOutput++;
				}

				cOutStage = 0;
			}
		}
		else
		{
			if (cZeroCounter != 0)
			{
				*pOutput = 0xE0 + cZeroCounter;
				pOutput++;

				cZeroCounter = 0;				
			}

			if (cOutStage == 0)
			{
				cOutChar = 0xFF;				
			}
			else
			{
				cOutChar += 0x0F;
				cOutStage = 0;
			}

			*pOutput = cOutChar;
			pOutput++;		

			if (nAbsDiffValue <= 63)
			{
				nDiffValue += 192;

				*pOutput = (XnUInt8)nDiffValue;
				pOutput++;
			}
			else
			{
				*(XnUInt16*)pOutput = XN_PREPARE_VAR16_IN_BUFFER((nCurrValue << 8) + (nCurrValue >> 8));
				pOutput+=2;
			}
		}

		nLastValue = nCurrValue;
		pInput++;
	}

	if (cOutStage != 0)
	{
		*pOutput = cOutChar + 0x0D;
		pOutput++;
	}

	if (cZeroCounter != 0)
	{
		*pOutput = 0xE0 + cZeroCounter;
		pOutput++;
	}

	*pnOutputSize = (XnUInt32)(pOutput - pOrigOutput);

	// All is good...
	return (XN_STATUS_OK);
}

XnStatus DE XnStreamCompressImage8Z(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize)
{
	// Local function variables
	const XnUInt8* pInputEnd = pInput + nInputSize;
	const XnUInt8* pOrigOutput = pOutput;
	XnUInt8 nCurrValue = 0;
	XnUInt8 nLastValue = 0;
	XnUInt8 nAbsDiffValue = 0;
	XnInt8 nDiffValue = 0;
	XnUInt8 cOutStage = 0;
	XnUInt8 cOutChar = 0;
	XnUInt8 cZeroCounter = 0;
	XnBool bFlag = FALSE;

	// Note: this function does not make sure it stay within the output memory boundaries!

	// Validate the input/output pointers (to make sure none of them is NULL)
	XN_VALIDATE_INPUT_PTR(pInput);
	XN_VALIDATE_INPUT_PTR(pOutput);
	XN_VALIDATE_INPUT_PTR(pnOutputSize);

	// Encode the data...
	nLastValue = *pInput;
	*pOutput = nLastValue;
	pInput++;
	pOutput++;

	while (pInput != pInputEnd)
	{	
		nCurrValue = *pInput;

		nDiffValue = (nLastValue - nCurrValue);
		nAbsDiffValue = (XnUInt8)abs(nDiffValue);

		if (nAbsDiffValue <= 6)
		{
			nDiffValue += 6;

			if (cOutStage == 0)
			{
				cOutChar = nDiffValue << 4;

				cOutStage = 1;
			}
			else
			{
				cOutChar += nDiffValue;

				if ((cOutChar == 0x66) && (bFlag == FALSE))
				{
					cZeroCounter++;

					if (cZeroCounter == 15)
					{
						*pOutput = 0xEF;
						pOutput++;

						cZeroCounter = 0;
					}
				}
				else
				{
					if (cZeroCounter != 0)
					{
						*pOutput = 0xE0 + cZeroCounter;
						pOutput++;

						cZeroCounter = 0;
					}

					*pOutput = cOutChar;
					pOutput++;

					bFlag = FALSE;
				}

				cOutStage = 0;
			}
		}
		else
		{
			if (cZeroCounter != 0)
			{
				*pOutput = 0xE0 + cZeroCounter;
				pOutput++;

				cZeroCounter = 0;				
			}

			if (cOutStage == 0)
			{
				cOutChar = 0xF0;		
				cOutChar += nCurrValue >> 4;

				*pOutput = cOutChar;
				pOutput++;		

				cOutChar = (nCurrValue & 0xF) << 4;
				cOutStage = 1;

				bFlag = TRUE;
			}
			else
			{
				cOutChar += 0x0F;
				cOutStage = 0;

				*pOutput = cOutChar;
				pOutput++;		

				*pOutput = nCurrValue;
				pOutput++;
			}
		}

		nLastValue = nCurrValue;
		pInput++;
	}

	if (cOutStage != 0)
	{
		*pOutput = cOutChar + 0x0D;
		pOutput++;
	}

	if (cZeroCounter != 0)
	{
		*pOutput = 0xE0 + cZeroCounter;
		pOutput++;
	}

	*pnOutputSize = (XnUInt32)(pOutput - pOrigOutput);

	// All is good...
	return (XN_STATUS_OK);
}

XnStatus DE XnStreamCompressConf4(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize)
{
	// Local function variables
	const XnUInt8* pInputEnd = pInput + nInputSize;
	const XnUInt8* pOrigOutput = pOutput;

	// Note: this function does not make sure it stay within the output memory boundaries!

	// Validate the input/output pointers (to make sure none of them is NULL)
	XN_VALIDATE_INPUT_PTR(pInput);
	XN_VALIDATE_INPUT_PTR(pOutput);
	XN_VALIDATE_INPUT_PTR(pnOutputSize);

	// Encode the data...
	while (pInput != pInputEnd)
	{
		*pOutput = *pInput << 4;
		pInput++;

		*pOutput += *pInput;
		pInput++;

		pOutput++;
	}

	*pnOutputSize = (XnUInt32)(pOutput - pOrigOutput);

	// All is good...
	return (XN_STATUS_OK);
}
}