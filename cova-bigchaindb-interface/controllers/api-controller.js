function get_unused_covaclave() {
    // TODO: In future we need to load balance
    // TODO: REPLACE HARDCODE
    return {url: "https://covaclave0.covalent.ai", success: true}
}

module.exports = {
	get_unused_covaclave
}