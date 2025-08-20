# 🎨 Nix for Humanity - Visual Architecture Guide

*Clear diagrams and visual representations of system architecture*

## 🏗️ System Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     🧑 USER INTERACTION LAYER                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Natural Language Input:  "install firefox"                    │
│                          "my wifi isn't working"               │
│                          "update my system"                    │
│                                                                 │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    🖥️ INTERFACE ADAPTATION LAYER                 │
├────────────┬────────────┬─────────────┬────────────────────────┤
│    CLI     │    TUI     │   Voice     │      REST API          │
│ (ask-nix)  │ (Textual)  │  (pipecat)  │    (FastAPI)          │
│            │            │             │                        │
│  Working   │  Planned   │   Future    │     Future            │
└────────────┴────────────┴─────────────┴────────────────────────┘
                             │
                   Unified Protocol
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    🧠 INTELLIGENCE ENGINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │    NLP      │  │   Learning   │  │   Personality    │     │
│  │  Pipeline   │  │    System    │  │   Adaptation     │     │
│  ├─────────────┤  ├──────────────┤  ├──────────────────┤     │
│  │ • Tokenize  │  │ • Patterns   │  │ • 10 Personas    │     │
│  │ • Intent    │  │ • Preferences│  │ • Style Switch   │     │
│  │ • Entities  │  │ • Evolution  │  │ • Context Aware  │     │
│  └─────────────┘  └──────────────┘  └──────────────────┘     │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │   Memory    │  │     XAI      │  │    Security      │     │
│  │   System    │  │   Engine     │  │    Layer         │     │
│  ├─────────────┤  ├──────────────┤  ├──────────────────┤     │
│  │ • Working   │  │ • Why        │  │ • Validation     │     │
│  │ • Episodic  │  │ • Confidence │  │ • Sandboxing     │     │
│  │ • Semantic  │  │ • Reasoning  │  │ • Permissions    │     │
│  └─────────────┘  └──────────────┘  └──────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    🔧 NIXOS INTEGRATION LAYER                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Current:              Target:                                  │
│  ┌──────────────┐     ┌────────────────────────┐              │
│  │  Subprocess  │ →   │  Native Python API     │              │
│  │   Commands   │     │  (nixos-rebuild-ng)    │              │
│  │              │     │                        │              │
│  │ • Slow       │     │ • 10x-1500x faster     │              │
│  │ • Timeouts   │     │ • Real-time progress   │              │
│  │ • Limited    │     │ • Full control         │              │
│  └──────────────┘     └────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow Diagram

```
User: "install firefox"
         │
         ↓
┌─────────────────┐
│ 1. Input Layer  │
│   Receive text  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐     ┌──────────────┐
│ 2. NLP Pipeline │────►│  Knowledge   │
│   Parse intent  │     │    Base      │
└────────┬────────┘     └──────────────┘
         │
         ↓
┌─────────────────┐     ┌──────────────┐
│ 3. Validation   │────►│  Security    │
│   Check safety  │     │   Rules      │
└────────┬────────┘     └──────────────┘
         │
         ↓
┌─────────────────┐     ┌──────────────┐
│ 4. Execution    │────►│   NixOS      │
│   Run command   │     │   System     │
└────────┬────────┘     └──────────────┘
         │
         ↓
┌─────────────────┐     ┌──────────────┐
│ 5. Learning     │────►│   User       │
│   Track pattern │     │  Profile     │
└────────┬────────┘     └──────────────┘
         │
         ↓
┌─────────────────┐
│ 6. Response     │
│   Format output │
└─────────────────┘
         │
         ↓
    User sees:
"Installing Firefox...
✓ Firefox installed successfully!
You can launch it from your applications menu."
```

## 🧩 Component Interaction Map

```
                    ┌─────────────────┐
                    │   User Input    │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         ┌──────▼──────┐          ┌──────▼──────┐
         │    CLI      │          │     TUI     │
         │  Adapter    │          │   Adapter   │
         └──────┬──────┘          └──────┬──────┘
                │                         │
                └───────────┬─────────────┘
                            │
                    ┌───────▼────────┐
                    │  Core Engine   │
                    │ (luminous_nix) │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
│  NLP Module    │ │ Learning Module │ │Security Module │
├────────────────┤ ├─────────────────┤ ├────────────────┤
│• IntentRecog   │ │• PatternTracker │ │• InputValidator│
│• EntityExtract │ │• PreferencesMgr │ │• CommandValid  │
│• TypoCorrect   │ │• Adaptation     │ │• PermissionChk │
└────────────────┘ └─────────────────┘ └────────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │ NixOS Commands │
                    │   Execution    │
                    └────────────────┘
```

## 📊 Data Model Overview

```
┌──────────────────────────────────────────────────────────┐
│                    User Profile                          │
├──────────────────────────────────────────────────────────┤
│ user_id: unique_identifier                               │
│ preferences: {                                           │
│   response_style: "friendly",                            │
│   verbosity: "medium",                                   │
│   expertise_level: "beginner"                           │
│ }                                                        │
│ interaction_history: [...]                               │
│ learned_patterns: [...]                                  │
└──────────────────────────────────────────────────────────┘
                    │
                    │ 1:many
                    ↓
┌──────────────────────────────────────────────────────────┐
│                    Interactions                          │
├──────────────────────────────────────────────────────────┤
│ interaction_id: unique_identifier                        │
│ timestamp: datetime                                      │
│ raw_input: "install firefox"                            │
│ recognized_intent: IntentType.INSTALL                    │
│ entities: {package: "firefox"}                          │
│ execution_result: Result                                 │
│ user_feedback: optional                                  │
└──────────────────────────────────────────────────────────┘
                    │
                    │ many:many
                    ↓
┌──────────────────────────────────────────────────────────┐
│                  Learning Patterns                       │
├──────────────────────────────────────────────────────────┤
│ pattern_id: unique_identifier                            │
│ pattern_type: "command_sequence"                         │
│ occurrences: count                                       │
│ confidence: 0.0-1.0                                      │
│ last_seen: datetime                                      │
└──────────────────────────────────────────────────────────┘
```

## 🚦 Implementation Status Visual

```
Component Status Legend:
✅ Complete/Working
🚧 In Progress
📅 Planned
❌ Not Started

┌─────────────────────────────────────────────────────────┐
│                  CURRENT STATUS                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  User Interfaces:                                       │
│  ├─ ✅ CLI (basic commands work)                       │
│  ├─ 🚧 TUI (files exist, not connected)               │
│  ├─ ❌ Voice (planned with pipecat)                    │
│  └─ ❌ API (future)                                    │
│                                                         │
│  Core Features:                                         │
│  ├─ ✅ Intent Recognition (70% accuracy)               │
│  ├─ ✅ Basic Execution (with issues)                   │
│  ├─ ✅ Security Validation                             │
│  ├─ 🚧 Knowledge Base (limited)                        │
│  └─ ✅ Personality System (5 styles)                   │
│                                                         │
│  Advanced Features:                                     │
│  ├─ ❌ Learning Pipeline (logging only)                │
│  ├─ ❌ Memory System                                   │
│  ├─ ❌ XAI Explanations                                │
│  ├─ ❌ Voice Interface                                 │
│  └─ ❌ Federated Learning                              │
│                                                         │
│  Infrastructure:                                        │
│  ├─ ✅ Python Package Structure                        │
│  ├─ 🚧 Test Coverage (25%)                            │
│  ├─ 🚧 Native NixOS API                               │
│  └─ ✅ Documentation (100%)                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Development Priority Matrix

```
                    Impact on Users
                    Low         High
         ┌─────────┬────────────┬─────────┐
    Low  │   📅    │            │   🚧    │
         │ Future  │            │ Current │
Effort   │Features │            │  Focus  │
         ├─────────┼────────────┼─────────┤
         │         │    ✅      │   📅    │
    High │   ❌    │ Complete   │  Next   │
         │  Skip   │            │ Priority│
         └─────────┴────────────┴─────────┘

Current Focus (🚧):
• Native Python-Nix API
• Connect TUI to backend
• Fix command reliability
• Increase test coverage

Next Priority (📅):
• Basic learning system
• Voice prototype
• XAI integration
• Memory system

Future Features:
• Federated learning
• Advanced personas
• GUI interface
• AR/VR support
```

## 🔐 Security Architecture Layers

```
┌─────────────────────────────────────────┐
│         User Input: "rm -rf /"         │
└────────────────┬───────────────────────┘
                 │
        Layer 1: Input Validation
                 ↓
┌─────────────────────────────────────────┐
│     ❌ Dangerous pattern detected       │
│     Suggestion: "Use remove command"    │
└─────────────────────────────────────────┘

Safe Input: "remove old-package"
                 │
        Layer 2: Intent Validation
                 ↓
┌─────────────────────────────────────────┐
│     ✅ Valid intent: REMOVE_PACKAGE     │
│     Entity: package="old-package"      │
└────────────────┬───────────────────────┘
                 │
        Layer 3: Permission Check
                 ↓
┌─────────────────────────────────────────┐
│     ✅ User has permission             │
│     Operation: remove single package    │
└────────────────┬───────────────────────┘
                 │
        Layer 4: Command Validation
                 ↓
┌─────────────────────────────────────────┐
│     ✅ Safe command structure          │
│     nix-env -e old-package             │
└────────────────┬───────────────────────┘
                 │
        Layer 5: Sandboxed Execution
                 ↓
┌─────────────────────────────────────────┐
│     Execute with limited permissions    │
│     Monitor for unexpected behavior     │
│     ✅ Success: Package removed        │
└─────────────────────────────────────────┘
```

## 🌊 The Sacred Trinity Development Flow

```
┌────────────────┐     ┌─────────────────┐     ┌──────────────┐
│     Human      │     │   AI Assistant  │     │ Domain Expert│
│   (Tristan)    │     │    (Claude)     │     │ (Local LLM)  │
├────────────────┤     ├─────────────────┤     ├──────────────┤
│ • Vision       │     │ • Architecture  │     │ • NixOS      │
│ • User needs   │ ←→  │ • Implementation│ ←→  │ • Best       │
│ • Testing      │     │ • Documentation │     │   practices  │
│ • Validation   │     │ • Synthesis     │     │ • Edge cases │
└────────────────┘     └─────────────────┘     └──────────────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                │
                        ┌───────▼────────┐
                        │  Nix for       │
                        │  Humanity      │
                        │                │
                        │ $200/month     │
                        │ Enterprise     │
                        │ Quality        │
                        └────────────────┘
```

---

*This visual guide complements the [Unified Architecture Overview](UNIFIED_ARCHITECTURE_OVERVIEW.md) with clear diagrams showing system structure, data flow, and implementation status.*