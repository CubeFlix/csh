#include <stdio.h>
#include <time.h>
#include <windows.h>

int main() {
	/* dumb silly stuff */

	/* console handles and other nonsense */
	HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
	CONSOLE_SCREEN_BUFFER_INFO consoleInfo;
	WORD saved_attributes;

	/* save console color attributes */
	GetConsoleScreenBufferInfo(hConsole, &consoleInfo);
	saved_attributes = consoleInfo.wAttributes;
	
	int b = 0;
	printf("VALORANT.EXE ENCOUNTERED AN ERROR: %x\nFull dump below \\/\n", &b);

	for (int i = 0; i < 5; i++) {
		SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN);
		printf("%i: ", (int)time(NULL));

		SetConsoleTextAttribute(hConsole, FOREGROUND_RED);	
		printf("ERROR - CRITICAL: [FAILED TO TERMINATE CHILDREN]\n");
	}

	/* some more nonsense */
	SetConsoleTextAttribute(hConsole, saved_attributes);
	int a = 0;
	printf("Must kill chilren manually || %x", &a);
	return 0;

	/* useless stuff */
}
