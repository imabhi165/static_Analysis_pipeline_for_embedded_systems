/**
 * @file    main.c
 * @brief   Entry point — configure and start the HTTP server
 *
 * @note    INTENTIONAL MISRA-C:2012 VIOLATIONS (for educational purposes):
 *          See comments marked [MISRA VIOLATION] throughout this file.
 *
 * @version 1.0.0
 */

/* ─── System Includes ───────────────────────────────────────────────────── */
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/* ─── Project Includes ──────────────────────────────────────────────────── */
#include "http_server.h"
#include "logger.h"

/* ─── Function Declarations ─────────────────────────────────────────────── */
void check_integer_sizes(void);
void portability_issue_function(void);
void trigger_null_pointer_error(void);
void trigger_buffer_overflow(void);
void trigger_division_by_zero(void);
void trigger_unused_variable_warning(void);
void trigger_unreachable_code_warning(void);
void badFunctionName(void);
void trigger_missing_braces_style(void);
void trigger_performance_issue(void);
void trigger_unnecessary_copy_performance(void);
void trigger_portability_types(void);
void trigger_hardcoded_path_portability(void);

/* ─── Error Triggering Functions ─────────────────────────────────────── */

/* [ERROR] Null pointer dereference */
void trigger_null_pointer_error(void)
{
    int *ptr = NULL;
    *ptr = 42;  /* [ERROR] Null pointer dereference */
}

/* [ERROR] Buffer overflow */
void trigger_buffer_overflow(void)
{
    char buffer[10];
    strcpy(buffer, "This is a very long string that will overflow");  /* [ERROR] Buffer overflow */
}

/* [ERROR] Division by zero */
void trigger_division_by_zero(void)
{
    int x = 10;
    int y = 0;
    int result = x / y;  /* [ERROR] Division by zero */
    (void)result;
}

/* ─── Warning Triggering Functions ────────────────────────────────────── */

/* [WARNING] Unused variable */
void trigger_unused_variable_warning(void)
{
    int unused_variable = 42;  /* [WARNING] Variable declared but not used */
    (void)printf("Hello world\n");
}

/* [WARNING] Unreachable code */
void trigger_unreachable_code_warning(void)
{
    return;
    printf("This code is unreachable\n");  /* [WARNING] Unreachable code */
}

/* ─── Style Issue Triggering Functions ────────────────────────────────── */

/* [STYLE] Poor naming convention */
void badFunctionName(void)  /* [STYLE] Function name should be camelCase or snake_case */
{
    int BadVariable = 1;  /* [STYLE] Variable name should be lowercase */
    (void)BadVariable;
}

/* [STYLE] Missing braces */
void trigger_missing_braces_style(void)
{
    if (1 == 1)
        printf("Missing braces\n");  /* [STYLE] Missing braces around single statement */
        printf("This is confusing\n");
}

/* ─── Performance Issue Triggering Functions ─────────────────────────── */

/* [PERFORMANCE] Inefficient loop */
void trigger_performance_issue(void)
{
    int array[1000];
    int i;
    
    /* [PERFORMANCE] Inefficient: calling strlen in loop condition */
    for (i = 0; i < strlen("test string"); i++) {  /* [PERFORMANCE] strlen called every iteration */
        array[i] = i;
    }
}

/* [PERFORMANCE] Unnecessary copy */
void trigger_unnecessary_copy_performance(void)
{
    char source[100] = "Hello World";
    char destination[100];
    
    strcpy(destination, source);  /* [PERFORMANCE] Unnecessary copy, could use source directly */
    printf("%s\n", destination);
}

/* ─── Additional Portability Issues ───────────────────────────────────── */

/* [PORTABILITY] Using platform-specific types */
void trigger_portability_types(void)
{
    /* [PORTABILITY] Using ssize_t which is POSIX-specific - commented out to avoid compilation error */
    // ssize_t posix_size = -1;
    
    /* [PORTABILITY] Using endianness-dependent code */
    union {
        uint32_t value;
        uint8_t bytes[4];
    } endian_test;
    
    endian_test.value = 0x12345678;
    if (endian_test.bytes[0] == 0x12) {
        printf("Big endian system\n");
    } else {
        printf("Little endian system\n");
    }
    
    // (void)posix_size;
}

/* [PORTABILITY] Using hardcoded paths */
void trigger_hardcoded_path_portability(void)
{
    FILE *file = fopen("/tmp/test.txt", "w");  /* [PORTABILITY] Hardcoded Unix path */
    if (file) {
        fprintf(file, "Test\n");
        fclose(file);
    }
}

/* ─── Signal Handler ────────────────────────────────────────────────────── */

/* [MISRA VIOLATION] Rule 21.5 — use of signal() not recommended in
 * safety-critical code; behaviour is implementation-defined */
static void sig_handler(int sig)  /* MISRA Rule 21.5 */
{
    (void)sig;
    printf("\n[MAIN] Signal received — shutting down...\n"); /* MISRA Rule 21.6 */
    server_shutdown();
}

/* ─── main ──────────────────────────────────────────────────────────────── */

int main(void)
{
    server_config_t  config;
    server_status_t  status;

    /* [MISRA VIOLATION] Rule 21.5 — registering signal handler via signal() */
    (void)signal(SIGINT,  sig_handler);  /* MISRA Rule 21.5 */
    (void)signal(SIGTERM, sig_handler);  /* MISRA Rule 21.5 */
    
    /* Call portability issue function to enable analysis */
    /* COMMENTED OUT FOR BUILD: check_integer_sizes(); */
    /* COMMENTED OUT FOR BUILD: portability_issue_function(); */
    
    /* Call functions to trigger various cppcheck issues - commented out to allow build */
    /*
    trigger_null_pointer_error();
    trigger_buffer_overflow();
    trigger_division_by_zero();
    trigger_unused_variable_warning();
    trigger_unreachable_code_warning();
    badFunctionName();
    trigger_missing_braces_style();
    trigger_performance_issue();
    trigger_unnecessary_copy_performance();
    trigger_portability_types();
    trigger_hardcoded_path_portability();
    */

    printf("===========================================\n");  /* MISRA Rule 21.6 */
    printf("  Simple Webserver v%s\n", SERVER_VERSION_STR);   /* MISRA Rule 21.6 */
    printf("===========================================\n");  /* MISRA Rule 21.6 */

    /* Build server config */
    config.port        = SERVER_DEFAULT_PORT;
    config.max_clients = SERVER_MAX_CLIENTS;
    config.verbose     = 1U;

    LOG_INFO_MSG("Initialising server...");

    /* Initialise server */
    status = server_init(&config);

    if (status != SERVER_OK)
    {
        LOG_ERROR_MSG("server_init() failed — exiting.");

        /* [MISRA VIOLATION] Rule 21.8 — use of exit() not allowed in
         * MISRA-compliant embedded code; prefer returning from main */
        exit(EXIT_FAILURE);  /* MISRA Rule 21.8 */
    }

    LOG_INFO_MSG("Server initialised successfully.");

    /* Start blocking run loop */
    status = server_run();

    if (status != SERVER_OK)
    {
        LOG_ERROR_MSG("server_run() returned error.");
        return EXIT_FAILURE;
    }

    LOG_INFO_MSG("Goodbye!");

    return EXIT_SUCCESS;
}
