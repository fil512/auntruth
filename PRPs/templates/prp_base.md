name: "Base Smile PRP Template v1 - Context-Rich with Validation Loops"
description: |

## Purpose
Template optimized for AI agents to implement code changes to Smile CDR and hapi-fhir with sufficient context and self-validation capabilities to achieve working code through iterative refinement.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
[What needs to be changed - be specific about the end state and desires]

## What
[User-visible behavior and technical requirements]

### Success Criteria
- [ ] [Specific measurable outcomes]

## All Needed Context

### Documentation & References (list all context needed to implement the feature)
```yaml
# MUST READ - Include these in your context window
- url: [Official API docs URL]
  why: [Specific sections/methods you'll need]
  
- file: [path/to/Example.java]
  why: [Pattern to follow, gotchas to avoid]
  
- doc: [Library documentation URL] 
  section: [Specific section about common pitfalls]
  critical: [Key insight that prevents common errors]

- docfile: [hapi-fhir-docs/src/main/resources/ca/uhn/hapi/fhir/docs/section/file.md]
  why: [hapi-fhir docs relevant to this change]

- docfile: [cdr-docs/src/main/resources/ca/cdr/docs/section/file.md]
  why: [cdr docs relevant to this change]
```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase
```bash

```

### Desired Codebase tree with files to be added and responsibility of file
```bash

```

### Known Gotchas of our codebase & Library Quirks
```java
// CRITICAL: [Library name] requires [specific setup]
// Example: DaoTest requires test to start H2
// Example: CDA Exchange Plus integration test requires Smile CDR App to be running
```

## Implementation Blueprint

### list of tasks to be completed to fullfill the PRP in the order they should be completed.

Ensure this process encapsulates the Test-Driven Development process described in CLAUDE.md

```yaml
Task 1:
MODIFY cdr-consent/src/main/java/ca/cdr/consent/svc/ConsentDelegateFactory.java:
  - FIND pattern: "MultiDelegateConsentService.withParallelVoting"
  - INJECT after line containing "aches.putConsentService"
  - PRESERVE existing method signatures

CREATE cdr-consent/src/main/java/ca/cdr/consent/svc/ConsentDelegateFactoryBuilder.java:
  - MIRROR pattern from: cdr-consent/src/main/java/ca/cdr/consent/svc/SomeOtherFactoryBuilder.java
  - MODIFY class name and core logic
  - KEEP error handling pattern identical

...(...)

Task N:
...

```


### Per task pseudocode as needed added to each task
```java

// Task 1 Begin with failing test
// Pseudocode with CRITICAL details dont write entire code

// Add new test method to cdr-app-test-3/src/test/java/ca/cdr/app/gateway/GatewayDiagnosticsIT.java
@Test
public void testNewCase() {
	// description of new case to be tested.
}

// PATTERN: Always validate input first
    Objects.requireNonNull(theChapter);
    
// GOTCHA: All ITs require specific setup, best achieved by extending BaseIT
public class BatchIT extends BaseIT {
}
// GOTCHA: FHIR Resource model classes require custom json serialization
ObjectMapper myObjectMapper = new CdrObjectMapper(ourFhirContext);
```

### Integration Points
```yaml
 CONFIG:
  - add to: cdr-api/src/main/java/ca/cdr/api/script/exec/graal/GraalSettings.java
  - pattern: @ConfigItem(
  
 IT TEST PROPERTIES:
  - add to: cdr-app-test-3/src/test/resources/cdr-config-unittest-gateway-connection.properties
  - pattern: "module.persistence.config.key = value"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
mvn spotless:apply                   # Format code
mvn checkstyle:check                 # Style checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns

Describe Unit and Integration tests following the `Testing Guidelines` section of CLAUDE.md as guidance.

```bash
# Run and iterate until passing:
mvn test -Dtest=CdaDocumentTranslatorTest -pl cdr-cda-exchange-2
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Run existing integration tests to ensure no regressions:
mvn test -Dtest=CdaExchangeRedesignR4IT -pl cdr-app-test-2

# Focus on this specific test method:
mvn test -Dtest=CdaExchangeRedesignR4IT#test_cda_to_fhir_with_parameterized_pre_post -pl cdr-app-test-2

# Expected: Tests pass, especially with preProcess=true parameter
# If failing: Check logs for pre-processing script execution
```

## Final validation Checklist
- [ ] All tests in changed modules pass: `mvn install -pl cdr-camel,cdr-broker`
- [ ] Code style clean: `mvn spotless:apply && mvn checkstyle:check`
- [ ] Error cases handled gracefully
- [ ] Logs are informative but not verbose
- [ ] Documentation updated if needed

---

## Anti-Patterns to Avoid
- ❌ Don't create new patterns when existing ones work
- ❌ Don't skip validation because "it should work"  
- ❌ Don't ignore failing tests - fix them
- ❌ Don't hardcode values that should be config
- ❌ Don't catch all exceptions - be specific
