/**
 * ==========================================================================
 * CITYVOTES TEMPLATE - STATIC DATA API
 * ==========================================================================
 *
 * Loads data from static JSON files in the data/ folder.
 * No backend needed - works with any static hosting.
 *
 * TO USE:
 * 1. Place your JSON data files in the data/ folder
 * 2. Follow the schemas in data/README.md
 * 3. This file works as-is - no changes needed
 *
 * ==========================================================================
 */

const DATA_BASE_PATH = 'data';
const API_TIMEOUT = 15000;

const CityVotesAPI = {
    /**
     * Validate that an ID is a positive integer
     */
    validateId(id, fieldName = 'ID') {
        const parsed = parseInt(id, 10);
        if (isNaN(parsed) || parsed < 1 || parsed > 100000) {
            throw new Error(`Invalid ${fieldName}: must be a positive integer`);
        }
        return parsed;
    },

    /**
     * Generic fetch handler for static JSON files with timeout
     */
    async fetchJSON(path) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

        try {
            const response = await fetch(`${DATA_BASE_PATH}/${path}`, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Not found');
                }
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timed out. Please try again.');
            }
            console.error(`Error loading ${path}:`, error);
            throw error;
        }
    },

    // ==================== Stats ====================

    /** Get overall statistics */
    async getStats() {
        return this.fetchJSON('stats.json');
    },

    // ==================== Council ====================

    /** Get all council members with stats */
    async getCouncil() {
        return this.fetchJSON('council.json');
    },

    /** Get individual council member details */
    async getCouncilMember(memberId) {
        const validId = this.validateId(memberId, 'council member ID');
        return this.fetchJSON(`council/${validId}.json`);
    },

    // ==================== Meetings ====================

    /** Get all meetings */
    async getMeetings() {
        return this.fetchJSON('meetings.json');
    },

    /** Get individual meeting with full agenda (voted + non-voted items) */
    async getMeeting(meetingId) {
        const validId = this.validateId(meetingId, 'meeting ID');
        return this.fetchJSON(`meetings/${validId}.json`);
    },

    // ==================== Votes ====================

    /** Get votes index with available years */
    async getVotesIndex() {
        return this.fetchJSON('votes-index.json');
    },

    /** Get votes for a specific year */
    async getVotesByYear(year) {
        const validYear = parseInt(year, 10);
        if (isNaN(validYear) || validYear < 2000 || validYear > 2100) {
            throw new Error('Invalid year');
        }
        return this.fetchJSON(`votes-${validYear}.json`);
    },

    /** Get all votes */
    async getVotes() {
        return this.fetchJSON('votes.json');
    },

    /** Get individual vote details */
    async getVote(voteId) {
        const validId = this.validateId(voteId, 'vote ID');
        return this.fetchJSON(`votes/${validId}.json`);
    },

    // ==================== Alignment ====================

    /** Get voting alignment data between council members */
    async getAlignment() {
        return this.fetchJSON('alignment.json');
    },

    // ==================== Dashboard Helpers ====================

    /** Get vote summary statistics */
    async getVoteSummary() {
        const [stats, votes] = await Promise.all([
            this.getStats(),
            this.getVotes()
        ]);

        const votesData = votes.votes;
        const outcomes = { PASS: 0, FAIL: 0, FLAG: 0 };

        votesData.forEach(v => {
            if (outcomes.hasOwnProperty(v.outcome)) {
                outcomes[v.outcome]++;
            }
        });

        return {
            success: true,
            summary: {
                total_votes: stats.stats.total_votes,
                total_meetings: stats.stats.total_meetings,
                date_range: stats.stats.date_range,
                outcomes: outcomes,
                pass_rate: ((outcomes.PASS / stats.stats.total_votes) * 100).toFixed(1)
            }
        };
    },

    /** Get member analysis data */
    async getMemberAnalysis() {
        return this.getCouncil();
    },

    /** Get member profile by ID */
    async getMemberProfile(memberId) {
        return this.getCouncilMember(memberId);
    },

    /** Get non-voted agenda items (high-importance) for search */
    async getNonVotedAgendaItems() {
        return this.fetchJSON('agenda-items.json');
    },

    /** Get agenda items (votes list) */
    async getAgendaItems() {
        return this.getVotes();
    },

    /** Get agenda item detail (vote detail) */
    async getAgendaItemDetail(itemId) {
        return this.getVote(itemId);
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CityVotesAPI };
}
