#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h> // VIOLATION: stdlib.h (Rule 21.3 - dynamic memory)
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <setjmp.h> // VIOLATION: setjmp.h (Rule 21.4 - non-local jumps)
 
/* --- GLOBAL SCOPE VIOLATIONS --- */
int g_status; // VIOLATION: External variable not explicitly initialized (Rule 9.1)
static char * g_msg; // VIOLATION: Use of char* instead of const char* (Rule 8.13)
jmp_buf env; // VIOLATION: Global jump buffer (Rule 21.4)
float threshold = 0.5f; // VIOLATION: Global floating point (Rule 1.1)
 
// VIOLATION: Function with no prototype (Rule 8.2)
void process_raw_data(data) 
int data;
{
    g_status = data + 1; // VIOLATION: Side effect in function (Advisory)
}
 
// VIOLATION: Recursion is strictly forbidden (Rule 17.2)
int safety_check_depth(int d) {
    if (d == 0) return 0;
    return 1 + safety_check_depth(d - 1);
}
 
int main(int argc, char **argv) {
    /* --- INITIALIZATION & DYNAMIC MEMORY (ERRORS) --- */
    // 25+ distinct malloc calls (Violating Rule 21.3 - No heap usage)
    int *p10 = (int*)malloc(sizeof(int)); 
    int *p11 = (int*)malloc(sizeof(int)); 
    int *p12 = (int*)malloc(sizeof(int)); 
    int *p13 = (int*)malloc(sizeof(int)); 
    int *p14 = (int*)malloc(sizeof(int)); 
    int *p15 = (int*)malloc(sizeof(int)); 
    int *p16 = (int*)malloc(sizeof(int)); 
    int *p17 = (int*)malloc(sizeof(int)); 
    int *p18 = (int*)malloc(sizeof(int)); 
    int *p19 = (int*)malloc(sizeof(int)); 
    int *p20 = (int*)malloc(sizeof(int)); 
    int *p21 = (int*)malloc(sizeof(int)); 
    int *p22 = (int*)malloc(sizeof(int)); 
    int *p23 = (int*)malloc(sizeof(int)); 
    int *p24 = (int*)malloc(sizeof(int)); 
    int *p25 = (int*)malloc(sizeof(int)); 
    int *p26 = (int*)malloc(sizeof(int)); 
    int *p27 = (int*)malloc(sizeof(int)); 
    int *p28 = (int*)malloc(sizeof(int)); 
    int *p29 = (int*)malloc(sizeof(int)); 
    int *p30 = (int*)malloc(sizeof(int)); 
    int *p31 = (int*)malloc(sizeof(int)); 
    int *p32 = (int*)malloc(sizeof(int)); 
    int *p33 = (int*)malloc(sizeof(int)); 
    int *p34 = (int*)malloc(sizeof(int));
 
    // VIOLATION: Pointer arithmetic (Rule 18.4)
    int *danger_ptr = p10 + 5;
 
    // VIOLATION: Goto for flow control (Rule 15.1)
    if (argc < 1) goto fail_early;
 
    /* --- LOGIC & TYPE WARNINGS --- */
    // 25+ Implicit type conversions (Violating Rule 10.3)
    double v40 = 40.5; int i40 = v40;
    double v41 = 41.5; int i41 = v41;
    double v42 = 42.5; int i42 = v42;
    double v43 = 43.5; int i43 = v43;
    double v44 = 44.5; int i44 = v44;
    double v45 = 45.5; int i45 = v45;
    double v46 = 46.5; int i46 = v46;
    double v47 = 47.5; int i47 = v47;
    double v48 = 48.5; int i48 = v48;
    double v49 = 49.5; int i49 = v49;
    double v50 = 50.5; int i50 = v50;
    double v51 = 51.5; int i51 = v51;
    double v52 = 52.5; int i52 = v52;
    double v53 = 53.5; int i53 = v53;
    double v54 = 54.5; int i54 = v54;
    double v55 = 55.5; int i55 = v55;
    double v56 = 56.5; int i56 = v56;
    double v57 = 57.5; int i57 = v57;
    double v58 = 58.5; int i58 = v58;
    double v59 = 59.5; int i59 = v59;
    double v60 = 60.5; int i60 = v60;
    double v61 = 61.5; int i61 = v61;
    double v62 = 62.5; int i62 = v62;
    double v63 = 63.5; int i63 = v63;
    double v64 = 64.5; int i64 = v64;
 
    // VIOLATION: Bitwise on signed types (Rule 10.1)
    int signed_mask = -1;
    int masked = signed_mask << 2;
 
    /* --- CONTROL FLOW & STYLE --- */
    for(int i=0; i<100; i++) {
        if (i == 50) continue; // VIOLATION: Continue statement (Rule 15.5)
        if (i == 90) break;    // VIOLATION: Break statement (Rule 15.4)
        // VIOLATION: Deeply nested if without braces (Rule 15.6)
        if (i > 10)
            if (i < 20)
                printf("Nested Output\n");
    }
 
    /* --- LIBGPIOD WITH BAD PRACTICE --- */
    struct gpiod_chip *chip = gpiod_chip_open("/dev/gpiochip4");
    // VIOLATION: Assignment in conditional (Rule 13.4)
    struct gpiod_line_request *req;
    if ((req = NULL)) { g_status = 1; }
 
    /* --- 300+ LINES OF MAGIC NUMBERS & STYLE VIOLATIONS --- */
    // Rule 4.1 (Magic Numbers) and Rule 15.7 (Missing Else)
    int temp_100 = 100 * 3;
    if (temp_100 == 103) { g_status = 103; } // No else block
    int var_101 = 101;
    int var_102 = 102;
    /* VIOLATION: Block comment /* nested */ */
    int var_104 = 104;
    int var_105 = 105;
    int var_106 = 106;
 
    // Repetitive logic to meet length and violation count
    int temp_120 = 120 * 3;
    if (temp_120 == 123) { g_status = 123; }
    int var_121 = 121;
    int var_122 = 122;
    /* VIOLATION: Block comment /* nested */ */
    int var_124 = 124;
    int var_125 = 125;
    // ... [Content repeats with incrementing magic numbers to reach ~500 lines] ...
    int temp_450 = 450 * 3;
    if (temp_450 == 453) { g_status = 453; }
    int var_451 = 451;
    int var_452 = 452;
    /* VIOLATION: Block comment /* nested */ */
    int var_454 = 454;
    int var_455 = 455;
    int var_456 = 456;
    int var_457 = 457;
    int var_458 = 458;
    int var_459 = 459;
 
    int temp_470 = 470 * 3;
    if (temp_470 == 473) { g_status = 473; }
    int var_471 = 471;
    int var_472 = 472;
    /* VIOLATION: Block comment /* nested */ */
    int var_474 = 474;
    int var_475 = 475;
    int var_476 = 476;
    int var_477 = 477;
    int var_478 = 478;
    int var_479 = 479;
 
fail_early:
    // VIOLATION: Multiple return points in a single function (Rule 17.4)
    return 0;
}