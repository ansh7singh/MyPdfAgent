"""
Page Ordering Agent
Determines the correct order of jumbled PDF pages using embeddings and LLM reasoning

Responsibilities:
- Analyze page content to determine logical order
- Use semantic embeddings to find page relationships
- Use LLM to make final ordering decisions
- Handle edge cases (empty pages, duplicates, etc.)
"""
import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from .llmAgent import LLMAgent

logger = logging.getLogger(__name__)


class PageOrderingAgent:
    """
    Agent for determining the correct order of jumbled PDF pages.
    
    Uses a hybrid approach:
    1. Semantic embeddings to find page relationships
    2. LLM reasoning to determine logical flow
    3. Heuristics for edge cases (title pages, table of contents, etc.)
    """
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the Page Ordering Agent.
        
        Args:
            embedding_model: Sentence transformer model for embeddings
        """
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.llm_agent = LLMAgent(model="llama3:latest")
            logger.info(f"✅ PageOrderingAgent initialized with {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize PageOrderingAgent: {e}")
            raise
    
    def determine_page_order(
        self,
        pages: List[Dict[str, Any]],
        original_pdf_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determine the correct order of pages in a jumbled PDF.
        
        Args:
            pages: List of page dictionaries with:
                - page_number: Original page number
                - text: Extracted text content
                - is_empty: Whether page is empty
                - confidence: OCR confidence
            original_pdf_path: Path to original PDF (for reference)
            
        Returns:
            Dictionary with:
                - success: Whether ordering succeeded
                - ordered_pages: List of pages in correct order
                - page_order: List of original page numbers in correct order
                - confidence_scores: Confidence for each ordering decision
                - reasoning: LLM reasoning for the order
        """
        try:
            logger.info(f"🧠 Determining page order for {len(pages)} pages")
            
            # Filter out empty pages but keep track of them
            non_empty_pages = [p for p in pages if not p.get('is_empty', False)]
            empty_pages = [p for p in pages if p.get('is_empty', False)]
            
            if len(non_empty_pages) < 2:
                logger.warning("Not enough pages to reorder (need at least 2 non-empty pages)")
                return {
                    'success': True,
                    'ordered_pages': pages,
                    'page_order': [p['page_number'] for p in pages],
                    'confidence_scores': [1.0] * len(pages),
                    'reasoning': 'Not enough pages to reorder'
                }
            
            # Step 1: Create embeddings for all pages
            logger.info("📊 Creating semantic embeddings for pages...")
            page_texts = [p.get('text', '')[:2000] for p in non_empty_pages]  # Limit to 2000 chars per page
            embeddings = self.embedding_model.encode(page_texts, show_progress_bar=False)
            
            # Step 2: Calculate similarity matrix
            similarity_matrix = cosine_similarity(embeddings)
            
            # Step 3: Use embeddings to find likely page transitions
            transition_scores = self._calculate_transition_scores(
                non_empty_pages, 
                embeddings, 
                similarity_matrix
            )
            
            # Log original page order for debugging
            original_page_numbers = [p['page_number'] for p in non_empty_pages]
            logger.info(f"📋 Original page numbers in input: {original_page_numbers}")
            logger.info(f"📋 Original indices (0-based): {list(range(len(non_empty_pages)))}")
            
            # Step 4: Use LLM to determine logical order
            logger.info("🤖 Using LLM to determine logical page order...")
            llm_order = self._llm_determine_order(non_empty_pages, transition_scores)
            
            llm_order_indices = llm_order.get('order', [])
            logger.info(f"🤖 LLM returned order (indices): {llm_order_indices}")
            if llm_order_indices:
                llm_page_numbers = [non_empty_pages[i]['page_number'] for i in llm_order_indices if 0 <= i < len(non_empty_pages)]
                logger.info(f"🤖 LLM order (page numbers): {llm_page_numbers}")
            
            # Step 5: Combine embeddings and LLM results
            final_order = self._combine_ordering_results(
                non_empty_pages,
                llm_order,
                transition_scores
            )
            
            # Log what we got after combining
            final_page_numbers = [p['page_number'] for p in final_order]
            logger.info(f"📋 Final order after combining (page numbers): {final_page_numbers}")
            
            # Step 6: Reinsert empty pages at their original positions
            final_pages_with_empty = self._reinsert_empty_pages(
                final_order,
                empty_pages,
                pages
            )
            
            # Ensure all pages have original_index for tracking
            for i, page in enumerate(final_pages_with_empty):
                if 'original_index' not in page:
                    page['original_index'] = i
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(
                final_pages_with_empty,
                transition_scores,
                llm_order
            )
            
            # Get the actual reordered page numbers (original page numbers in new order)
            page_order = [p['page_number'] for p in final_pages_with_empty]
            original_order = [p['page_number'] for p in pages]
            
            # Log the actual reordering
            logger.info(f"✅ Page order determined: {page_order}")
            logger.info(f"   Original order: {original_order}")
            
            # Check if order actually changed
            if page_order == original_order:
                logger.warning("⚠️  Page order is the same as original - pages may already be in correct order, or reordering failed")
                # Try to detect if pages are actually jumbled by checking if LLM returned different order
                llm_order_indices = llm_order.get('order', list(range(len(non_empty_pages))))
                if llm_order_indices != list(range(len(non_empty_pages))):
                    logger.warning(f"   LLM suggested different order: {llm_order_indices}, but final order is unchanged")
            else:
                logger.info(f"   ✅ Order changed: {original_order} -> {page_order}")
            
            return {
                'success': True,
                'ordered_pages': final_pages_with_empty,
                'page_order': page_order,  # Original page numbers in new order
                'confidence_scores': confidence_scores,
                'reasoning': llm_order.get('reasoning', 'Ordering based on semantic similarity and LLM analysis'),
                'original_order': original_order,
                'reordered_indices': [p.get('original_index', i) for i, p in enumerate(final_pages_with_empty)],
                'llm_order_indices': llm_order.get('order', [])  # Add LLM indices for debugging
            }
            
        except Exception as e:
            logger.error(f"Error determining page order: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'ordered_pages': pages,  # Return original order on failure
                'page_order': [p['page_number'] for p in pages],
                'confidence_scores': [0.5] * len(pages)
            }
    
    def _calculate_transition_scores(
        self,
        pages: List[Dict],
        embeddings: np.ndarray,
        similarity_matrix: np.ndarray
    ) -> Dict[Tuple[int, int], float]:
        """
        Calculate scores for potential page transitions.
        
        Higher scores indicate more likely sequential pages.
        """
        transition_scores = {}
        
        for i in range(len(pages)):
            for j in range(len(pages)):
                if i != j:
                    # Use semantic similarity as base
                    semantic_score = similarity_matrix[i][j]
                    
                    # Boost score if pages seem to flow together
                    # (e.g., one page ends with a question, next starts with answer)
                    text_i = pages[i].get('text', '')[:500]  # First 500 chars
                    text_j = pages[j].get('text', '')[:500]  # First 500 chars
                    
                    flow_score = self._calculate_flow_score(text_i, text_j)
                    
                    # Combined score
                    transition_scores[(i, j)] = (semantic_score * 0.6) + (flow_score * 0.4)
        
        return transition_scores
    
    def _calculate_flow_score(self, text_before: str, text_after: str) -> float:
        """Calculate how well text_before flows into text_after."""
        if not text_before or not text_after:
            return 0.0
        
        # Simple heuristics for flow
        text_before_lower = text_before.lower().strip()
        text_after_lower = text_after.lower().strip()
        
        # Check for continuation patterns
        flow_indicators = [
            # First page indicators
            ('executive summary', 'problem statement'),
            ('introduction', 'methodology'),
            ('problem statement', 'solution'),
            ('abstract', 'introduction'),
            # Sequential indicators
            ('section 1', 'section 2'),
            ('part i', 'part ii'),
            ('chapter 1', 'chapter 2'),
            # Conclusion indicators
            ('conclusion', 'references'),
            ('summary', 'references'),
        ]
        
        for pattern_before, pattern_after in flow_indicators:
            if pattern_before in text_before_lower and pattern_after in text_after_lower:
                return 0.8
        
        # Check for Roman numeral sequences (Article I, II, III, etc.)
        import re
        roman_before = re.findall(r'\b(article|part|chapter)\s+([ivxlcdm]+)\b', text_before[:200], re.IGNORECASE)
        roman_after = re.findall(r'\b(article|part|chapter)\s+([ivxlcdm]+)\b', text_after[:200], re.IGNORECASE)
        
        if roman_before and roman_after:
            # Simple check: if we see Article I before and Article II after, that's good flow
            try:
                roman_numerals = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9, 'x': 10}
                last_roman = roman_before[-1][1].lower()
                first_roman = roman_after[0][1].lower()
                if last_roman in roman_numerals and first_roman in roman_numerals:
                    if roman_numerals[first_roman] == roman_numerals[last_roman] + 1:
                        return 0.7
            except:
                pass
        
        # Check for clause numbering sequences (i), ii), iii), etc. or 1), 2), 3), etc.
        clause_before = re.findall(r'([ivxlcdm]+)\)|(\d+)\)', text_before[:300], re.IGNORECASE)
        clause_after = re.findall(r'([ivxlcdm]+)\)|(\d+)\)', text_after[:300], re.IGNORECASE)
        
        if clause_before and clause_after:
            try:
                # Get the last clause number from before
                last_clause = None
                for match in clause_before:
                    if match[0]:  # Roman numeral
                        last_clause = match[0].lower()
                    elif match[1]:  # Arabic number
                        last_clause = int(match[1])
                
                # Get the first clause number from after
                first_clause = None
                for match in clause_after:
                    if match[0]:  # Roman numeral
                        first_clause = match[0].lower()
                    elif match[1]:  # Arabic number
                        first_clause = int(match[1])
                
                if last_clause and first_clause:
                    if isinstance(last_clause, str) and isinstance(first_clause, str):
                        # Both are Roman numerals
                        roman_numerals = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9, 'x': 10, 'xi': 11, 'xii': 12, 'xiii': 13, 'xiv': 14, 'xv': 15, 'xvi': 16, 'xvii': 17, 'xviii': 18, 'xix': 19, 'xx': 20}
                        if last_clause in roman_numerals and first_clause in roman_numerals:
                            if roman_numerals[first_clause] == roman_numerals[last_clause] + 1:
                                return 0.75
                    elif isinstance(last_clause, int) and isinstance(first_clause, int):
                        # Both are Arabic numbers
                        if first_clause == last_clause + 1:
                            return 0.7
            except:
                pass
        
        # Check for numbering sequences
        numbers_before = re.findall(r'\b(\d+)\b', text_before[:100])
        numbers_after = re.findall(r'\b(\d+)\b', text_after[:100])
        
        if numbers_before and numbers_after:
            try:
                last_num_before = int(numbers_before[-1])
                first_num_after = int(numbers_after[0])
                if first_num_after == last_num_before + 1:
                    return 0.6
            except:
                pass
        
        return 0.3  # Default flow score
    
    def _llm_determine_order(
        self,
        pages: List[Dict],
        transition_scores: Dict[Tuple[int, int], float]
    ) -> Dict[str, Any]:
        """Use LLM to determine logical page order."""
        try:
            # Prepare page summaries for LLM
            page_summaries = []
            for i, page in enumerate(pages):
                text = page.get('text', '')[:500]  # First 500 chars
                page_summaries.append({
                    'index': i,
                    'page_number': page['page_number'],
                    'summary': text[:200] + '...' if len(text) > 200 else text,
                    'first_words': text[:50] if text else ''
                })
            
            # Create prompt for LLM
            prompt = (
                "You are an AI assistant that reorders JUMBLED PDF pages.\n"
                "IMPORTANT: The pages below are OUT OF ORDER and need to be reordered.\n"
                "Do NOT assume they are already in the correct order - analyze the content carefully.\n\n"
                "Analyze the following pages and determine their correct logical order.\n"
                "Consider:\n"
                "- Title pages and table of contents typically come first\n"
                "- Introduction/Executive Summary comes before main content\n"
                "- Sections should follow a logical sequence (Article I, Article II, etc.)\n"
                "- Sequential numbering or references indicate order\n"
                "- Conclusion/Summary comes at the end\n"
                "- References/Appendices come last\n"
                "- For loan agreements: Title page → Definitions → Terms → Conditions → Signatures\n\n"
                "Pages to reorder (these are CURRENTLY OUT OF ORDER):\n"
            )
            
            for summary in page_summaries:
                text_preview = summary['summary'][:400]  # Show more text for better analysis
                # Show first few lines to help identify content
                lines = text_preview.split('\n')[:5]
                content_preview = '\n'.join(lines)
                prompt += f"\n[Index {summary['index']}] Page {summary['page_number']}:\n"
                prompt += f"{content_preview}\n"
                prompt += f"---\n"
            
            prompt += (
                "\n\n" + "="*80 + "\n"
                "CRITICAL INSTRUCTIONS:\n"
                "="*80 + "\n"
                "These pages are DEFINITELY JUMBLED and OUT OF ORDER.\n"
                "The PDF was scanned/merged incorrectly, so the page sequence is wrong.\n"
                "You MUST analyze the CONTENT of each page to determine the correct order.\n\n"
                "DO NOT assume pages are in order just because their indices are sequential.\n"
                "DO NOT return [0, 1, 2, 3...] - that would mean no reordering is needed.\n\n"
                "ANALYZE EACH PAGE'S CONTENT for:\n"
                "1. Title/Header text (e.g., 'LOAN AGREEMENT', 'ARTICLE I', 'DEFINITIONS')\n"
                "2. Section numbers or references (e.g., 'Article I' should come before 'Article II')\n"
                "3. Sequential content (e.g., definitions before terms, terms before conditions)\n"
                "4. Page numbers mentioned in the text itself\n"
                "5. Logical flow (introduction → main content → conclusion)\n\n"
                "For loan agreements, typical order is:\n"
                "1. Title page (LOAN AGREEMENT BETWEEN...)\n"
                "2. Definitions section\n"
                "3. Terms and conditions\n"
                "4. Specific clauses (Article I, II, III...)\n"
                "5. Signatures/Appendices\n\n"
                "You must respond with ONLY valid JSON in this exact format:\n"
                "{\"order\": [0, 2, 1, 3], \"reasoning\": \"Explanation here\"}\n"
                "Where 'order' is an array of page indices (0-based) in the correct sequence.\n"
                "Example: [0, 2, 1, 3] means:\n"
                "  - First: page at index 0\n"
                "  - Second: page at index 2\n"
                "  - Third: page at index 1\n"
                "  - Fourth: page at index 3\n"
                "The 'order' array must contain ALL page indices from 0 to " + str(len(pages) - 1) + " exactly once.\n"
                "If you return [0, 1, 2, 3...], you are saying pages are already in order - ONLY do this if you are 100% certain.\n"
                "Do not include any text before or after the JSON object.\n"
                "Response:\n"
            )
            
            # Query LLM
            result = self.llm_agent.query(user_prompt=prompt)
            
            if not result.get('success'):
                logger.warning(f"LLM query failed: {result.get('error')}")
                return {'order': list(range(len(pages))), 'reasoning': 'LLM query failed, using original order'}
            
            response = result.get('result', '')
            logger.debug(f"LLM raw response: {response[:500]}...")
            
            # Parse JSON from response
            import json
            import re
            
            # Try multiple parsing strategies
            parsed_order = None
            reasoning = 'Ordering based on logical flow'
            
            # Strategy 1: Look for JSON object with "order" field
            json_patterns = [
                r'\{[^{}]*"order"\s*:\s*\[[^\]]+\][^{}]*\}',  # JSON with order array
                r'\{.*?"order"\s*:\s*\[.*?\].*?\}',  # More flexible pattern
                r'\{.*?\}',  # Any JSON object
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                        parsed_order = parsed.get('order')
                        reasoning = parsed.get('reasoning', reasoning)
                        if parsed_order:
                            break
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.debug(f"Failed to parse JSON with pattern {pattern}: {e}")
                        continue
            
            # Strategy 2: Look for array of numbers directly
            if not parsed_order:
                array_patterns = [
                    r'\[[\s\d,]+\]',  # Simple array like [0, 1, 2, 3]
                    r'order\s*[:=]\s*\[[\s\d,]+\]',  # order: [0, 1, 2, 3]
                ]
                
                for pattern in array_patterns:
                    array_match = re.search(pattern, response, re.IGNORECASE)
                    if array_match:
                        try:
                            # Extract the array part
                            array_str = array_match.group(0)
                            if ':' in array_str or '=' in array_str:
                                array_str = array_str.split(':', 1)[-1].split('=', 1)[-1].strip()
                            parsed_order = json.loads(array_str)
                            if isinstance(parsed_order, list) and len(parsed_order) == len(pages):
                                break
                        except (json.JSONDecodeError, ValueError) as e:
                            logger.debug(f"Failed to parse array: {e}")
                            continue
            
            # Strategy 3: Extract reasoning even if order not found
            reasoning_match = re.search(r'reasoning["\']?\s*[:=]\s*["\']?([^"\']+)["\']?', response, re.IGNORECASE)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
            
            # Validate and return order
            if parsed_order and isinstance(parsed_order, list):
                # Convert to integers if needed
                try:
                    parsed_order = [int(x) for x in parsed_order]
                    # Validate order
                    if len(parsed_order) == len(pages) and set(parsed_order) == set(range(len(pages))):
                        logger.info(f"✅ Successfully parsed LLM order: {parsed_order}")
                        return {'order': parsed_order, 'reasoning': reasoning}
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid order format: {e}")
            
            # Fallback: use embedding-based ordering with better algorithm
            logger.warning("Could not parse LLM response, using embedding-based ordering")
            # Use transition scores to create a better ordering
            embedding_order = self._create_embedding_based_order(pages, transition_scores)
            return {'order': embedding_order, 'reasoning': 'LLM response not parseable, using embedding similarity analysis'}
            
        except Exception as e:
            logger.error(f"Error in LLM ordering: {e}", exc_info=True)
            return {'order': list(range(len(pages))), 'reasoning': f'Error: {str(e)}'}
    
    def _combine_ordering_results(
        self,
        pages: List[Dict],
        llm_order: Dict,
        transition_scores: Dict[Tuple[int, int], float]
    ) -> List[Dict]:
        """Combine LLM ordering with embedding-based scores."""
        llm_order_indices = llm_order.get('order', list(range(len(pages))))
        
        logger.info(f"🔄 Applying LLM order: {llm_order_indices}")
        
        # Check if LLM returned original order (which might indicate it didn't reorder)
        if llm_order_indices == list(range(len(pages))):
            logger.warning("⚠️  LLM returned original order [0, 1, 2, ...] - pages may not be reordered")
            logger.info("   Trying embedding-based ordering as alternative...")
            # Try embedding-based ordering instead
            embedding_order = self._create_embedding_based_order(pages, transition_scores)
            if embedding_order != list(range(len(pages))):
                logger.info(f"   Embedding-based order: {embedding_order}")
                llm_order_indices = embedding_order
            else:
                logger.warning("   Embedding-based order also returned original order")
        
        # Validate and create ordered pages
        ordered_pages = []
        seen_indices = set()
        for idx in llm_order_indices:
            if 0 <= idx < len(pages):
                if idx in seen_indices:
                    logger.warning(f"⚠️  Duplicate index {idx} in LLM order, skipping")
                    continue
                seen_indices.add(idx)
                page_copy = pages[idx].copy()
                page_copy['original_index'] = idx
                ordered_pages.append(page_copy)
        
        # If LLM order is invalid or incomplete, use transition scores to create a path
        if len(ordered_pages) != len(pages):
            logger.warning(f"⚠️  LLM order incomplete ({len(ordered_pages)}/{len(pages)} pages), using transition scores")
            ordered_pages = self._create_path_from_transitions(pages, transition_scores)
        
        # Log the final order
        final_page_nums = [p['page_number'] for p in ordered_pages]
        logger.info(f"✅ Final ordered page numbers: {final_page_nums}")
        
        return ordered_pages
    
    def _create_path_from_transitions(
        self,
        pages: List[Dict],
        transition_scores: Dict[Tuple[int, int], float]
    ) -> List[Dict]:
        """Create an ordering path using transition scores (greedy path finding)."""
        if not pages:
            return []
        
        # Start with page that has highest outgoing transition scores
        # (likely a beginning page)
        start_page = 0
        max_outgoing = sum(
            transition_scores.get((0, j), 0) for j in range(len(pages))
        )
        
        for i in range(1, len(pages)):
            outgoing = sum(
                transition_scores.get((i, j), 0) for j in range(len(pages))
            )
            if outgoing > max_outgoing:
                max_outgoing = outgoing
                start_page = i
        
        # Greedy path: always go to next page with highest transition score
        ordered_indices = [start_page]
        remaining = set(range(len(pages))) - {start_page}
        
        while remaining:
            current = ordered_indices[-1]
            best_next = None
            best_score = -1
            
            for next_idx in remaining:
                score = transition_scores.get((current, next_idx), 0)
                if score > best_score:
                    best_score = score
                    best_next = next_idx
            
            if best_next is not None:
                ordered_indices.append(best_next)
                remaining.remove(best_next)
            else:
                # No good transition, add remaining pages in order
                ordered_indices.extend(sorted(remaining))
                break
        
        # Create ordered pages
        ordered_pages = []
        for idx in ordered_indices:
            page_copy = pages[idx].copy()
            page_copy['original_index'] = idx
            ordered_pages.append(page_copy)
        
        return ordered_pages
    
    def _create_embedding_based_order(
        self,
        pages: List[Dict],
        transition_scores: Dict[Tuple[int, int], float]
    ) -> List[int]:
        """Create an ordering based on embedding similarity (returns list of indices)."""
        if not pages or len(pages) <= 1:
            return list(range(len(pages)))
        
        # Find the best starting page (likely a title/intro page)
        # Look for pages with words like "LOAN AGREEMENT", "ARTICLE - I", "DEFINITIONS", etc.
        start_candidates = []
        for i, page in enumerate(pages):
            text = page.get('text', '').upper()
            score = 0
            # Title page indicators (strong signals)
            if 'LOAN AGREEMENT' in text and 'BETWEEN' in text:
                score += 20
            if 'LOAN AGREEMENT' in text:
                score += 15
            if 'ARTICLE' in text and ('I' in text[:100] or '1' in text[:100] or 'ONE' in text[:100]):
                score += 12
            if 'DEFINITIONS' in text:
                score += 10
            if text.startswith('LOAN AGREEMENT'):
                score += 15
            # Check for title-like patterns at the start
            first_lines = text.split('\n')[:3]
            for line in first_lines:
                if 'AGREEMENT' in line and len(line) < 100:
                    score += 8
                if 'BETWEEN' in line and 'AND' in line:
                    score += 8
            # Penalize pages with continuation markers (likely not first page)
            if text.startswith('-') or text.startswith('...'):
                score -= 5
            if 'CONTINUED' in text[:200] or 'CONTINUATION' in text[:200]:
                score -= 3
            # Check if page seems like a middle page (mentions previous sections)
            if any(word in text[:200] for word in ['AS SET FORTH', 'AS PROVIDED', 'PURSUANT TO']):
                score -= 2
            
            start_candidates.append((score, i))
        
        # Sort by score and pick the best starting page
        start_candidates.sort(reverse=True)
        start_page = start_candidates[0][1] if start_candidates else 0
        
        # Build ordering using transition scores
        ordered_indices = [start_page]
        remaining = set(range(len(pages))) - {start_page}
        
        # Greedy path: always go to next page with highest transition score
        while remaining:
            current = ordered_indices[-1]
            best_next = None
            best_score = -1
            
            for next_idx in remaining:
                score = transition_scores.get((current, next_idx), 0)
                if score > best_score:
                    best_score = score
                    best_next = next_idx
            
            if best_next is not None and best_score > 0.3:  # Only follow if score is reasonable
                ordered_indices.append(best_next)
                remaining.remove(best_next)
            else:
                # No good transition, add remaining pages in order
                ordered_indices.extend(sorted(remaining))
                break
        
        return ordered_indices
    
    def _reinsert_empty_pages(
        self,
        ordered_pages: List[Dict],
        empty_pages: List[Dict],
        all_original_pages: List[Dict]
    ) -> List[Dict]:
        """
        Reinsert empty pages at their original positions relative to the reordered sequence.
        
        IMPORTANT: This preserves the reordered order of non-empty pages.
        Empty pages are inserted based on their original positions relative to non-empty pages.
        """
        if not empty_pages:
            # No empty pages, return ordered pages as-is
            logger.info("No empty pages to reinsert")
            return ordered_pages
        
        logger.info(f"Reinserting {len(empty_pages)} empty pages into reordered sequence")
        
        # Create a mapping of page numbers to their original positions
        original_positions = {p['page_number']: i for i, p in enumerate(all_original_pages)}
        
        # Create mappings for quick lookup
        empty_pages_map = {p['page_number']: p for p in empty_pages}
        non_empty_page_numbers = {p['page_number'] for p in ordered_pages}
        
        # CRITICAL: We must preserve the REORDERED order of non-empty pages
        # and only insert empty pages at their original positions relative to the reordered sequence
        
        # Start with reordered pages in their new order
        result = list(ordered_pages)  # This preserves the reordered sequence!
        
        # Now insert empty pages at their original positions relative to non-empty pages
        # We need to find where each empty page should go in the reordered sequence
        empty_pages_map = {p['page_number']: p for p in empty_pages}
        
        # For each empty page, find its position in the original order
        # and insert it at the corresponding position in the reordered sequence
        for empty_page in empty_pages:
            empty_page_num = empty_page['page_number']
            empty_original_pos = original_positions.get(empty_page_num, -1)
            
            if empty_original_pos < 0:
                continue
            
            # Find where to insert: find the first non-empty page that came after
            # this empty page in the original order
            insert_position = len(result)  # Default: append at end
            
            for i, ordered_page in enumerate(ordered_pages):
                ordered_page_num = ordered_page['page_number']
                ordered_original_pos = original_positions.get(ordered_page_num, 9999)
                
                # If this ordered page came after the empty page originally,
                # insert the empty page before it
                if ordered_original_pos > empty_original_pos:
                    # Find the position of this ordered page in result
                    for j, page in enumerate(result):
                        if page['page_number'] == ordered_page_num:
                            insert_position = j
                            break
                    break
            
            # Insert the empty page at the found position
            result.insert(insert_position, empty_page)
            logger.debug(f"Inserted empty page {empty_page_num} at position {insert_position}")
        
        logger.info(f"Final result: {len(result)} pages ({len([p for p in result if p['page_number'] in non_empty_page_numbers])} non-empty + {len(empty_pages)} empty)")
        final_page_nums = [p['page_number'] for p in result]
        logger.info(f"Final page order: {final_page_nums}")
        
        return result
    
    def _calculate_confidence_scores(
        self,
        ordered_pages: List[Dict],
        transition_scores: Dict[Tuple[int, int], float],
        llm_order: Dict
    ) -> List[float]:
        """Calculate confidence scores for the ordering."""
        confidence_scores = []
        
        for i in range(len(ordered_pages)):
            page = ordered_pages[i]
            
            # Empty pages get lower confidence
            if page.get('is_empty', False):
                confidence_scores.append(0.5)
                continue
            
            if i == 0:
                # First page: confidence based on whether it looks like a start
                confidence = 0.7  # Default
            elif i < len(ordered_pages):
                # Confidence based on transition score from previous page
                prev_page = ordered_pages[i-1]
                prev_idx = prev_page.get('original_index', i-1)
                curr_idx = page.get('original_index', i)
                
                # Only calculate transition if both pages are non-empty
                if not prev_page.get('is_empty', False) and not page.get('is_empty', False):
                    transition_score = transition_scores.get((prev_idx, curr_idx), 0.5)
                    confidence = min(1.0, transition_score + 0.2)  # Boost slightly
                else:
                    confidence = 0.6
            else:
                confidence = 0.6
            
            confidence_scores.append(confidence)
        
        return confidence_scores

