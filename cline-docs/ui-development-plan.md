# Development Plan for Streamlit Chat Interface

## Project Purpose and Goals

The goal is to create a lightweight, user-friendly chat interface using Streamlit that allows interactive communication with the existing crewAI product research system. This will transform the current command-line tool into an accessible web-based chat application for conducting product comparisons through natural conversation.

## Context and Background

The existing system is a well-structured crewAI application with:
- Three specialised agents (researcher, analyst, comparison_agent)
- YAML-based configuration for agents and tasks
- Integration with OpenRouter API and Serper API
- Command-line interface that accepts 2-5 products for comparison
- Markdown report generation with comprehensive error handling
- Robust validation and testing framework

The Streamlit interface will wrap this existing functionality without requiring major architectural changes to the core system.

## Hard Requirements

- Must integrate with existing `ProductResearchCrew` class without modification
- Must maintain all existing error handling and validation
- Must support natural language input for product comparison requests
- Must display research progress and final results
- Must allow downloading of generated reports
- Must handle API key configuration securely
- Must be lightweight and suitable for single-user deployment

## Development Phases

### Phase 1: Core Streamlit Setup and Integration
- [x] Add Streamlit to requirements.txt with latest stable version
- [x] Create main Streamlit application file (`src/ui/streamlit_app.py`)
- [x] Set up basic page configuration and layout
- [x] Implement session state management for conversation history
- [x] Create basic chat interface with input and message display
- [x] Test basic Streamlit functionality
- [x] Organise UI code under `/src/ui` directory structure

### Phase 2: CrewAI Integration Layer
- [ ] Create wrapper class to interface between Streamlit and ProductResearchCrew
- [ ] Implement natural language parsing to extract product names from chat input
- [ ] Add input validation for product comparison requests
- [ ] Integrate existing error handling system with Streamlit error display
- [ ] Test integration with mock data

### Phase 3: Chat Interface Implementation
- [ ] Implement chat message display with proper formatting
- [ ] Add typing indicators and progress bars for long-running operations
- [ ] Create conversation flow for product comparison requests
- [ ] Add support for follow-up questions and clarifications
- [ ] Implement message history persistence within session
- [ ] Add clear conversation functionality

### Phase 4: Results Display and Download
- [ ] Create markdown renderer for comparison reports
- [ ] Implement expandable sections for detailed results
- [ ] Add download functionality for generated reports
- [ ] Create visual indicators for different types of responses
- [ ] Add copy-to-clipboard functionality for results
- [ ] Test results display with various report formats

### Phase 5: Configuration and Environment Setup
- [ ] Implement secure API key configuration through Streamlit secrets
- [ ] Add environment variable fallback for API keys
- [ ] Create configuration validation on startup
- [ ] Add system status indicators
- [ ] Implement graceful error handling for missing configurations
- [ ] Test with different configuration scenarios

### Phase 6: User Experience Enhancements
- [ ] Add welcome message and usage instructions
- [ ] Implement example prompts and suggestions
- [ ] Add loading animations and progress feedback
- [ ] Create responsive layout for different screen sizes
- [ ] Add keyboard shortcuts for common actions
- [ ] Implement conversation export functionality

### Phase 7: Testing and Validation
- [ ] Create unit tests for Streamlit integration components
- [ ] Test chat interface with various input formats
- [ ] Validate error handling in web interface
- [ ] Test concurrent usage scenarios
- [ ] Perform end-to-end testing with real API calls
- [ ] Test deployment scenarios

### Phase 8: Documentation and Deployment
- [ ] Update README.md with Streamlit usage instructions
- [ ] Create deployment guide for local and cloud deployment
- [ ] Add troubleshooting section to documentation
- [ ] Create user guide with screenshots
- [ ] Add configuration examples
- [ ] Test deployment instructions

## Assumptions and Unknowns

- Assuming single-user deployment (no multi-user authentication needed)
- Assuming existing API rate limits are sufficient for web interface usage
- May need to implement request queuing if multiple comparisons are requested simultaneously
- Streamlit's session state behaviour with long-running operations may require testing

## QA Checklist

- [ ] All user instructions followed
- [ ] Streamlit interface integrates seamlessly with existing crewAI system
- [ ] No modifications required to core ProductResearchCrew functionality
- [ ] All existing error handling and validation preserved
- [ ] Chat interface handles various input formats gracefully
- [ ] Progress indication works correctly for long-running operations
- [ ] Report download and display functionality works reliably
- [ ] API key configuration is secure and well-documented
- [ ] Code follows existing project conventions and British English spelling
- [ ] All new functionality has appropriate unit tests
- [ ] Documentation is comprehensive and accurate
- [ ] Deployment instructions are tested and verified
- [ ] Performance is acceptable for single-user scenarios
- [ ] Security considerations addressed for web deployment
