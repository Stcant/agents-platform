# Security reference

Check against the real code, not in the abstract.

## Trust boundaries

- Where does external data enter (HTTP, CLI, file, queue, environment, another service)? Is it validated there, with the type and range the code actually assumes?
- Is validation applied on the server or in the trusted layer, not only in the client?
- Are errors returned to users free of internal paths, stack traces and sensitive values?

## Access control

- Authentication answers "who"; authorization answers "may this principal act on this specific resource". Is the resource check present, not just a route guard?
- Can an identifier from the request select another user's object? Check ownership on read and write.
- Are administrative or debug endpoints protected by the same rules as normal endpoints?

## Injection and unsafe input

- Are queries parameterized? Is dynamic SQL or NoSQL built from strings anywhere?
- Is shell invocation avoided, or are arguments passed without a shell? Are user-controlled paths resolved and checked against traversal?
- Is rendered output escaped by default? Are raw-HTML escapes justified and sanitized?
- Are uploaded files checked for type, size and destination? Are they stored outside executable paths?
- Are outbound requests to user-supplied URLs restricted to intended schemes and hosts (SSRF)?

## Secrets and data at rest

- Are credentials read from configuration or a secret store, never hardcoded or logged?
- Are tokens, keys and personal data absent from logs, examples, fixtures and error messages?
- Is cryptography from a maintained library with current parameters, not a homemade scheme?

## Dependencies

- Does a new dependency have a maintained release, a compatible license, and a reason to exist? Do not add one for trivial work.
