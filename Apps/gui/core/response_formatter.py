#!/usr/bin/env python3
"""
Response Formatter Module

This module provides advanced formatting capabilities for VidSage responses,
including tables, lists, comparisons, structured data, and intelligent formatting.
"""

import re
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """Types of responses that can be formatted"""
    COMPARISON = "comparison"
    LIST = "list"
    TABLE = "table"
    PROCESS = "process"
    DEFINITION = "definition"
    ANALYSIS = "analysis"
    SUMMARY = "summary"
    QA = "qa"
    TECHNICAL = "technical"

@dataclass
class FormattingContext:
    """Context for response formatting"""
    question_type: ResponseType
    key_concepts: List[str]
    has_numbers: bool
    has_comparisons: bool
    has_steps: bool
    technical_terms: List[str]

class ResponseFormatter:
    """Advanced response formatter for VidSage"""
    
    def __init__(self):
        """Initialize the response formatter"""
        self.comparison_keywords = [
            'vs', 'versus', 'compare', 'difference', 'better', 'worse',
            'advantages', 'disadvantages', 'pros', 'cons', 'contrast'
        ]
        
        self.list_keywords = [
            'list', 'enumerate', 'types', 'kinds', 'categories', 'examples',
            'benefits', 'features', 'characteristics', 'points'
        ]
        
        self.process_keywords = [
            'how to', 'steps', 'process', 'procedure', 'method', 'way',
            'approach', 'instructions', 'guide', 'tutorial'
        ]
        
        self.technical_keywords = [
            'algorithm', 'function', 'code', 'implementation', 'technical',
            'programming', 'development', 'architecture', 'system'
        ]
    
    def analyze_question(self, question: str) -> FormattingContext:
        """
        Analyze a question to determine the best formatting approach
        
        Args:
            question: User question to analyze
            
        Returns:
            FormattingContext with analysis results
        """
        question_lower = question.lower()
        
        # Detect question type
        question_type = ResponseType.QA  # Default
        
        if any(keyword in question_lower for keyword in self.comparison_keywords):
            question_type = ResponseType.COMPARISON
        elif any(keyword in question_lower for keyword in self.list_keywords):
            question_type = ResponseType.LIST
        elif any(keyword in question_lower for keyword in self.process_keywords):
            question_type = ResponseType.PROCESS
        elif any(keyword in question_lower for keyword in self.technical_keywords):
            question_type = ResponseType.TECHNICAL
        elif 'what is' in question_lower or 'define' in question_lower:
            question_type = ResponseType.DEFINITION
        
        # Extract key concepts (nouns and important words)
        key_concepts = self._extract_key_concepts(question)
        
        # Detect structural elements
        has_numbers = bool(re.search(r'\d+', question))
        has_comparisons = any(keyword in question_lower for keyword in self.comparison_keywords)
        has_steps = any(keyword in question_lower for keyword in self.process_keywords)
        
        # Extract technical terms
        technical_terms = [term for term in key_concepts if any(tech in term.lower() for tech in self.technical_keywords)]
        
        return FormattingContext(
            question_type=question_type,
            key_concepts=key_concepts,
            has_numbers=has_numbers,
            has_comparisons=has_comparisons,
            has_steps=has_steps,
            technical_terms=technical_terms
        )
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b[A-Za-z]{3,}\b', text)
        
        # Filter out common words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
            'did', 'use', 'way', 'she', 'many', 'oil', 'sit', 'set', 'run', 'eat'
        }
        
        return [word for word in words if word.lower() not in stop_words]
    
    def format_response(self, raw_response: str, context: FormattingContext) -> str:
        """
        Format a raw response based on the formatting context
        
        Args:
            raw_response: Raw response from the AI
            context: Formatting context
            
        Returns:
            Formatted response with appropriate structure
        """
        # Clean the response first
        cleaned_response = self._clean_response(raw_response)
        
        # Apply formatting based on context
        if context.question_type == ResponseType.COMPARISON:
            return self._format_comparison(cleaned_response, context)
        elif context.question_type == ResponseType.LIST:
            return self._format_list(cleaned_response, context)
        elif context.question_type == ResponseType.PROCESS:
            return self._format_process(cleaned_response, context)
        elif context.question_type == ResponseType.TECHNICAL:
            return self._format_technical(cleaned_response, context)
        elif context.question_type == ResponseType.DEFINITION:
            return self._format_definition(cleaned_response, context)
        else:
            return self._format_general(cleaned_response, context)
    
    def _clean_response(self, response: str) -> str:
        """Clean the response of unwanted elements"""
        # Remove timestamp markers
        cleaned = re.sub(r'\[\d{1,2}:\d{2}\]', '', response)
        # Remove "at the X mark" references
        cleaned = re.sub(r'at the \[\d{1,2}:\d{2}\] mark', '', cleaned)
        cleaned = re.sub(r'mentioned at the.*?mark', '', cleaned)
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _format_comparison(self, response: str, context: FormattingContext) -> str:
        """Format comparison responses with tables or structured comparisons"""
        # Try to detect comparison elements
        lines = response.split('\n')
        comparison_items = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['vs', 'versus', 'compared to', 'while']):
                comparison_items.append(line.strip())
        
        if len(comparison_items) >= 2:
            # Create a comparison table
            formatted = "## Comparison\n\n"
            formatted += "| Aspect | Details |\n"
            formatted += "|--------|----------|\n"
            
            for item in comparison_items:
                # Extract the comparison aspect and details
                parts = re.split(r'[:;-]', item, 1)
                if len(parts) == 2:
                    aspect = parts[0].strip()
                    details = parts[1].strip()
                    formatted += f"| {aspect} | {details} |\n"
            
            formatted += f"\n{response}"
        else:
            # Structure as comparison sections
            formatted = "## Comparison Analysis\n\n"
            formatted += self._add_structure_headers(response)
        
        return formatted
    
    def _format_list(self, response: str, context: FormattingContext) -> str:
        """Format list responses with proper bullet points or numbers"""
        lines = response.split('\n')
        formatted_lines = []
        
        in_list = False
        list_counter = 1
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Detect list items
            if re.match(r'^\d+[\.\)]', stripped) or stripped.startswith('•') or stripped.startswith('-'):
                if not in_list:
                    formatted_lines.append("## Key Points\n")
                    in_list = True
                
                # Ensure proper list formatting
                if not re.match(r'^\d+\.', stripped):
                    formatted_lines.append(f"{list_counter}. {stripped.lstrip('•-').strip()}")
                    list_counter += 1
                else:
                    formatted_lines.append(stripped)
            else:
                if in_list:
                    in_list = False
                    formatted_lines.append('')
                formatted_lines.append(stripped)
        
        return '\n'.join(formatted_lines)
    
    def _format_process(self, response: str, context: FormattingContext) -> str:
        """Format process/step-by-step responses"""
        # Look for numbered steps or process indicators
        lines = response.split('\n')
        formatted_lines = []
        
        step_counter = 1
        in_steps = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Detect step indicators
            if any(indicator in stripped.lower() for indicator in ['step', 'first', 'second', 'then', 'next', 'finally']):
                if not in_steps:
                    formatted_lines.append("## Process Steps\n")
                    in_steps = True
                
                # Format as numbered step
                if not re.match(r'^\d+\.', stripped):
                    formatted_lines.append(f"**Step {step_counter}:** {stripped}")
                    step_counter += 1
                else:
                    formatted_lines.append(f"**{stripped}**")
            else:
                if in_steps and step_counter > 1:
                    # This might be a description of the current step
                    formatted_lines.append(f"   - {stripped}")
                else:
                    formatted_lines.append(stripped)
        
        return '\n'.join(formatted_lines)
    
    def _format_technical(self, response: str, context: FormattingContext) -> str:
        """Format technical responses with code blocks and structured sections"""
        # Wrap technical terms and code in appropriate formatting
        formatted = response
        
        # Wrap code-like terms in backticks
        code_pattern = r'\b(function|class|method|variable|algorithm|API|JSON|XML|HTTP|URL)\b'
        formatted = re.sub(code_pattern, r'`\1`', formatted, flags=re.IGNORECASE)
        
        # Add technical documentation structure
        if 'implementation' in response.lower() or 'code' in response.lower():
            formatted = "## Technical Overview\n\n" + formatted
            
            # Look for code snippets and wrap them
            lines = formatted.split('\n')
            in_code_block = False
            code_lines = []
            result_lines = []
            
            for line in lines:
                # Simple heuristic for code detection
                if ('(' in line and ')' in line and any(lang in line.lower() for lang in ['javascript', 'python', 'java', 'function'])):
                    if not in_code_block:
                        result_lines.append('```')
                        in_code_block = True
                    code_lines.append(line)
                else:
                    if in_code_block and code_lines:
                        result_lines.extend(code_lines)
                        result_lines.append('```')
                        code_lines = []
                        in_code_block = False
                    result_lines.append(line)
            
            if in_code_block and code_lines:
                result_lines.extend(code_lines)
                result_lines.append('```')
            
            formatted = '\n'.join(result_lines)
        
        return formatted
    
    def _format_definition(self, response: str, context: FormattingContext) -> str:
        """Format definition responses with clear structure"""
        lines = response.split('\n')
        formatted_lines = []
        
        # Find the main term being defined
        main_terms = context.key_concepts[:2]  # Take the first two key concepts
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Bold the main terms when they appear
            for term in main_terms:
                if term.lower() in stripped.lower() and i < 3:  # Only in first few lines
                    stripped = stripped.replace(term, f"**{term}**")
                    break
            
            formatted_lines.append(stripped)
        
        # Add definition structure
        if formatted_lines and not formatted_lines[0].startswith('##'):
            formatted_lines.insert(0, "## Definition\n")
        
        return '\n'.join(formatted_lines)
    
    def _format_general(self, response: str, context: FormattingContext) -> str:
        """Format general responses with improved structure"""
        # Add headers for better organization
        formatted = self._add_structure_headers(response)
        
        # Enhance key concepts with bold formatting
        for concept in context.key_concepts[:5]:  # Limit to first 5 concepts
            formatted = re.sub(f'\\b{re.escape(concept)}\\b', f"**{concept}**", formatted, count=1, flags=re.IGNORECASE)
        
        return formatted
    
    def _add_structure_headers(self, response: str) -> str:
        """Add structure headers to improve readability"""
        lines = response.split('\n')
        formatted_lines = []
        
        paragraph_count = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Add headers for new paragraphs (simple heuristic)
            if paragraph_count == 0 and len(stripped) > 50:
                formatted_lines.append("## Overview\n")
                paragraph_count += 1
            
            formatted_lines.append(stripped)
        
        return '\n'.join(formatted_lines)
    
    def create_summary_table(self, items: List[Dict[str, Any]], title: str = "Summary") -> str:
        """Create a formatted table for summary data"""
        if not items:
            return ""
        
        # Get all unique keys from items
        all_keys = set()
        for item in items:
            all_keys.update(item.keys())
        
        keys = list(all_keys)
        
        # Create table header
        table = f"## {title}\n\n"
        table += "| " + " | ".join(keys) + " |\n"
        table += "| " + " | ".join(["---"] * len(keys)) + " |\n"
        
        # Add table rows
        for item in items:
            row_values = [str(item.get(key, "")) for key in keys]
            table += "| " + " | ".join(row_values) + " |\n"
        
        return table
    
    def create_comparison_table(self, comparisons: List[Tuple[str, str, str]], 
                              headers: Tuple[str, str, str] = ("Item", "Aspect", "Details")) -> str:
        """Create a comparison table"""
        if not comparisons:
            return ""
        
        table = "## Comparison\n\n"
        table += f"| {headers[0]} | {headers[1]} | {headers[2]} |\n"
        table += "|" + "|".join(["---"] * 3) + "|\n"
        
        for item, aspect, details in comparisons:
            table += f"| {item} | {aspect} | {details} |\n"
        
        return table
