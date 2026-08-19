from enum import Enum


##########################################################################
# RESOURCE ENDPOINTS

class Endpoint(Enum):
    """Resource Endpoints"""
    
    #: String: Provides the data for the dataset. Advanced selection criteria,
    #: including filters, may be available depending on the dataset.
    DATA = "data"
    
    #: String: Provides the metadata for the dataset, including which fields
    #: are available, the data type of the field, and a description. The fields
    #: from this endpoint should match the members of a dataset's enum.
    METADATA = "metadata"
    
    #: String: Provides unique values, and versions of those values, for the
    #: partition field(s) of a dataset
    PARTITIONS = "partitions"
    
    #: String: Provides a comprehensive list of all Query API datasets,
    #: including version information, whether each dataset is currently active,
    #: and the various capabilities and features supported by each dataset.
    #: Responses follow the `Datasets schema
    #: <https://schemas.api.finra.org/FINRAApiPlatformDatasetsDetail.json>`__.
    DATASETS = "datasets"


##########################################################################
# DATASETS - QUERY API GROUPS

class Group(Enum):
    """Dataset API groups returned by :py:meth:`BaseClient.get_datasets`"""
    
    #: String: Equity API group. These datasets provide access to
    #: Over-the-Counter (OTC) trade and equity data.
    EQUITY = "otcMarket"
    
    #: String: Fixed Income API group. These datasets provide access to
    #: Over-the-Counter (OTC) secondary market transaction data for fixed
    #: income securities as reported to TRACE.
    FIXED_INCOME = "fixedIncomeMarket"
    
    #: String: FINRA API group. These datasets include data and content
    #: typically found on FINRA.org including the FINRA Rulebook.
    FINRA = "finra"
    
    #: String: Firm API group. These datasets provide access to information
    #: that is specific to individual FINRA member firms, some of which are
    #: involved in registration operations and only accessible by the firm
    #: itself.
    FIRM = "firm"
    
    #: String: Registration API group. These datasets provide member firms
    #: access to their registration records as stored in the Central
    #: Registration Depository (CRD).
    REGISTRATION = "registration"
    
    #: String: TRACE Report Card API group. These datasets provide access to
    #: FINRA TRACE Report Cards available via FINRA Report Center. Report Cards
    #: help firms detect potential compliance issues early and cover a variety
    #: of topics and rule sets. Learn more about `TRACE Report Cards
    #: <https://www.finra.org/compliance-tools/report-center>`__.
    REPORT_CARD = "reportcard"


##########################################################################
# EQUITY GROUP

class ATSBlockSummary(Enum):
    """Fields returned by :py:meth:`BaseClient.get_ats_block_summary`"""
    
    #: Date: **Partition Field**. Month Start Date.
    #: Format: yyyy-MM-dd
    MONTH_START_DATE = "monthStartDate"
    
    #: String: ATS MPID
    MPID = "MPID"
    
    #: String: ATS Market Participant name
    MARKET_PARTICIPANT_NAME = "marketParticipantName"
    
    #: Date: Start Date (First of the month) of the summary data.
    #: Format: yyyy-MM-dd
    SUMMARY_START_DATE = "summaryStartDate"
    
    #: Number: Total of all ATS trades (block and non-block) by ATS MPID
    TOTAL_TRADES = "totalTradeCount"
    
    #: Number: Total of all ATS shares traded (block and non-block) by ATS MPID
    TOTAL_VOLUME = "totalShareQuantity"
    
    #: Number: Based on the total of all ATS trades and shares traded
    #: (block and non-block) by ATS MPID
    AVERAGE_TRADE_SIZE = "averageTradeSize"
    
    #: Number: Rank of ATS Average Trade Size per ATS as compared to all other
    #: ATS MPIDs Average Trade Sizes
    AVERAGE_TRADE_SIZE_RANK = "averageTradeSizeRank"
    
    #: Number: Rank of ATS Trades Market Share per ATS MPID as compared to all
    #: other ATS MPIDs Market Share Trades (block and non-block)
    TRADE_RANK = "ATSTradeRank"
    
    #: Number: Rank of ATS Shares traded Market Share per ATS MPID as compared
    #: to all other ATS MPIDs' Market Share of Shares Traded
    #: (block and non-block)
    SHARE_RANK = "ATSShareRank"
    
    #: Number: Percentage of ATS Total Trades of the Grand Total of all ATS
    #: Trades by ATS MPID
    TRADE_PERCENT = "ATSTradePercent"
    
    #: Number: Percentage of ATS Total Shares of the Grand Total of all ATS
    #: Shares by ATS MPID
    SHARE_PERCENT = "ATSSharePercent"
    
    #: Number: Total ATS block counts
    BLOCK_TRADES = "ATSBlockCount"
    
    #: Number: Total ATS block share quantities
    BLOCK_VOLUME = "ATSBlockQuantity"
    
    #: Number: Based on the total of ATS Block trades and shares traded by ATS
    #: MPID
    AVERAGE_BLOCK_SIZE = "averageBlockSize"
    
    #: Number: Rank of ATS Average Block Trade Size per ATS MPID as compared to
    #: all other ATS MPIDs Average Block Trade Sizes
    AVERAGE_BLOCK_SIZE_RANK = "averageBlockSizeRank"
    
    #: Number: Rank of ATS Block Trade Market Share per ATS MPID as compared to
    #: all other ATS MPIDs Block Trades
    BLOCK_TRADE_RANK = "ATSBlockTradeRank"
    
    #: Number: Rank of ATS Block Market Share per ATS MPID as compared to all
    #: other ATS MPIDs Market Share of Shares Traded
    BLOCK_SHARE_RANK = "ATSBlockShareRank"
    
    #: Number: Average Block size Share Count Percentage
    BLOCK_TRADE_PERCENT = "ATSBlockTradePercent"
    
    #: Number: Average Block size Share Quantity Percentage
    BLOCK_SHARE_PERCENT = "ATSBlockSharePercent"
    
    #: Number: Percentage of ATS Block Trades of their ATS Total Trades by ATS
    #: MPID
    BLOCK_BUSINESS_TRADE_PERCENT = "ATSBlockBusinessTradePercent"
    
    #: Number: Percentage of ATS Block Shares Traded of their ATS Total Shares
    #: Traded by ATS MPID
    BLOCK_BUSINESS_SHARE_PERCENT = "ATSBlockBusinessSharePercent"
    
    #: Number: Rank of ATS Block Trade Business Share per ATS MPID as compared
    #: to all other ATS MPIDs Block Trades Business Share
    BLOCK_BUSINESS_TRADE_RANK = "ATSBlockBusinessTradeRank"
    
    #: Number: Rank of ATS Block Shares Traded Market Share per ATS MPID as
    #: compared to all other ATS MPIDs Block Shares Traded Business
    #: Share
    BLOCK_BUSINESS_SHARE_RANK = "ATSBlockBusinessShareRank"
    
    #: String: Summary Type. Possible values:
    #:
    #: - ``2K`` : 2K to 10K Shares
    #: - ``10K`` : 10K+ Shares
    #: - ``100K`` : $100K to $200K
    #: - ``200K`` : $200K+
    #: - ``10K-200K`` : 10K+ Shares AND $200K+
    #: - ``2K-100K`` : 2K to 10K Shares AND $100K to $200K
    SUMMARY_TYPE_CODE = "summaryTypeCode"
    
    #: String: Summary Type descriptions for the summary type codes
    SUMMARY_TYPE_DESCRIPTION = "summaryTypeDescription"
    
    #: Date: Most recent date on which total trades was updated based on data
    #: received from each ATS/OTC.
    #: Format: yyyy-MM-dd
    LAST_UPDATE_DATE = "lastUpdateDate"
    
    #: Date: This date represents the date of the first publication of the
    #: data, the first Monday or next business day of the following month.
    #: Format: yyyy-MM-dd
    INITIAL_PUBLISHED_DATE = "initialPublishedDate"
    
    #: Date: This date represents the last time a firm sent an update to any
    #: underlying data that contributes to the aggregate count.
    #: Format: yyyy-MM-dd
    LAST_REPORTED_DATE = "lastReportedDate"
    
    #: String: ATS or OTC (should always be ATS)
    ATS_OTC = "atsOtc"


class OTCBlockSummary(Enum):
    """Fields returned by :py:meth:`BaseClient.get_otc_block_summary`"""
    
    #: Date: **Partition Field**. Month Start Date.
    #: Format: yyyy-MM-dd
    MONTH_START_DATE = "monthStartDate"
    
    #: String: CRD firm name
    CRD_FIRM_NAME = "crdFirmName"
    
    #: Date: Start Date (first of the month) of the summary data.
    #: Format: yyyy-MM-dd
    SUMMARY_START_DATE = "summaryStartDate"
    
    #: Number: Total of all OTC trades (block and non-block) by OTC CRD
    TOTAL_TRADES = "totalTradeCount"
    
    #: Number: Total of all OTC shares traded (block and non-block) by OTC CRD
    TOTAL_VOLUME = "totalShareQuantity"
    
    #: Number: Based on the total of all OTC trades and shares traded
    #: (block and non-block) by OTC CRD
    AVERAGE_TRADE_SIZE = "averageTradeSize"
    
    #: Number: Rank of OTC Average Trade Size per OTC as compared to all other
    #: OTC CRDs Average Trade Sizes
    AVERAGE_TRADE_SIZE_RANK = "averageTradeSizeRank"
    
    #: Number: Rank of OTC Trades Market Share per OTC CRD as compared to all
    #: other OTC CRDs Market Share Trades (block and non-block)
    TRADE_RANK = "OTCTradeRank"
    
    #: Number: Rank of OTC Shares traded Market Share per OTC CRD as compared
    #: to all other OTC CRDs Market Share of Shares Traded
    #: (block and non-block)
    SHARE_RANK = "OTCShareRank"
    
    #: Number: Percentage of OTC Total Trades of the Grand Total of all OTC
    #: Trades by OTC CRD
    TRADE_PERCENT = "OTCTradePercent"
    
    #: Number: Percentage of OTC Total Shares of the Grand Total of all OTC
    #: Shares by OTC CRD
    SHARE_PERCENT = "OTCSharePercent"
    
    #: Number: Total OTC block counts
    BLOCK_TRADES = "OTCBlockCount"
    
    #: Number: Total OTC block share quantities
    BLOCK_VOLUME = "OTCBlockQuantity"
    
    #: Number: Based on the total of OTC Block trades & shares traded by OTC
    #: CRD
    AVERAGE_BLOCK_SIZE = "averageBlockSize"
    
    #: Number: Rank of OTC Average Block Trade Size per OTC CRD as compared to
    #: all other OTC CRDs Average Block Trade Sizes
    AVERAGE_BLOCK_SIZE_RANK = "averageBlockSizeRank"
    
    #: Number: Rank of OTC Block Trade Market Share per OTC CRD as compared to
    #: all other OTC CRDs Block Trades
    BLOCK_TRADE_RANK = "OTCBlockTradeRank"
    
    #: Number: Rank of OTC Block Market Share per OTC CRD as compared to all
    #: other OTC CRDs Market Share of Shares Traded
    BLOCK_SHARE_RANK = "OTCBlockShareRank"
    
    #: Number: Average Block size Share Count Percentage
    BLOCK_TRADE_PERCENT = "OTCBlockTradePercent"
    
    #: Number: Average Block size Share QuantityPercentage
    BLOCK_SHARE_PERCENT = "OTCBlockSharePercent"
    
    #: Number: Percentage of OTC Block Trades of their OTC Total Trades by
    #: OTC CRD
    BLOCK_BUSINESS_TRADE_PERCENT = "OTCBlockBusinessTradePercent"
    
    #: Number: Percentage of OTC Block Shares Traded of their OTC Total Shares
    #: Traded by OTC CRD
    BLOCK_BUSINESS_SHARE_PERCENT = "OTCBlockBusinessSharePercent"
    
    #: Number: Rank of OTC Block Trade Business Share per OTC CRD as compared
    #: to all other OTC CRDs Block Trades Business Share
    BLOCK_BUSINESS_TRADE_RANK = "OTCBlockBusinessTradeRank"
    
    #: Number: Rank of OTC Block Shares Traded Market Share per OTC CRD as
    #: compared to all other OTC CRDs Block Shares Traded Business
    #: Share
    BLOCK_BUSINESS_SHARE_RANK = "OTCBlockBusinessShareRank"
    
    #: String: Summary Type. Possible values:
    #:
    #: - ``2K`` : 2K to 10K Shares
    #: - ``10K`` : 10K+ Shares
    #: - ``100K`` : $100K to $200K
    #: - ``200K`` : $200K+
    #: - ``10K-200K`` : 10K+ Shares AND $200K+
    #: - ``2K-100K`` : 2K to 10K Shares AND $100K to $200K
    SUMMARY_TYPE_CODE = "summaryTypeCode"
    
    #: String: Summary Type descriptions for the summary type codes
    SUMMARY_TYPE_DESCRIPTION = "summaryTypeDescription"
    
    #: Date: Most recent date on which total trades was updated based on data
    #: received from each ATS/OTC.
    #: Format: yyyy-MM-dd
    LAST_UPDATE_DATE = "lastUpdateDate"
    
    #: Date: This date represents the date of the first publication of the
    #: data, the first Monday or next business day of the following month.
    #: Format: yyyy-MM-dd
    INITIAL_PUBLISHED_DATE = "initialPublishedDate"
    
    #: Date: This date represents the last time a firm sent an update to any
    #: underlying data that contributes to the aggregate count.
    #: Format: yyyy-MM-dd
    LAST_REPORTED_DATE = "lastReportedDate"
    
    #: String: ATS or OTC (should always be OTC)
    ATS_OTC = "atsOtc"


class ConsolidatedShortInterest(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_consolidated_short_interest`
    """
    
    #: Date: **Partition Field**. Settlement Date.
    #: Format: yyyy-MM-dd
    SETTLEMENT_DATE = "settlementDate"
    
    #: Number: Settlement Date for Shorts Cycle.
    #: Format: yyyyMMdd
    ACCOUNTING_YEAR_MONTH = "accountingYearMonthNumber"
    
    #: String: Security Symbol.
    #: Securities Information Processor Symbol Identifier.
    SYMBOL = "symbolCode"
    
    #: String: Name of the Issue
    ISSUE_NAME = "issueName"
    
    #: String: The issuer's service group exchange code
    GROUP_EXCHANGE_CODE = "issuerServicesGroupExchangeCode"
    
    #: String: The market class code
    MARKET_CLASS_CODE = "marketClassCode"
    
    #: Number: Short Position in the current cycle
    CURRENT_SHORT_POSITION = "currentShortPositionQuantity"
    
    #: Number: Short Position in the previous cycle
    PREVIOUS_SHORT_POSITION = "previousShortPositionQuantity"
    
    #: String: Flag indicating a stock split has taken place. It will either be
    #: a "S", if there was a split in the current shorts cycle, or null.
    STOCK_SPLIT_FLAG = "stockSplitFlag"
    
    #: Number: Average Daily Volume Quantity. Default value is 0. Excludes
    #: non-media trades.
    AVERAGE_DAILY_VOLUME = "averageDailyVolumeQuantity"
    
    #: Number: Days to Cover Quantity. Default value is 0.
    DAYS_TO_COVER = "daysToCoverQuantity"
    
    #: String: Will either be "R", if the short position for the prior cycle
    #: was revised, or null
    REVISION_FLAG = "revisionFlag"
    
    #: Number: Percent Change in Short Position between Previous Unadjusted and
    #: current Short Position, rounded to 2 decimal places. If there is
    #: no previous short position or if it is 0, then value will be 100.
    CHANGE_PERCENT = "changePercent"
    
    #: Number: Difference between Current Short Position and Previous
    #: Unadjusted Short Position
    CHANGE_PREVIOUS = "changePreviousNumber"


class DailyShortSaleVolume(Enum):
    """Fields returned by :py:meth:`BaseClient.get_daily_short_sale_volume`"""
    
    #: Date: **Partition Field**. Trade Date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: String: Security Symbol.
    #: Securities Information Processor Symbol Identifier.
    SYMBOL = "securitiesInformationProcessorSymbolIdentifier"
    
    #: Number: Aggregate reported share volume of executed short sale and short
    #: sale exempt trades during regular trading hours
    SHORT_VOLUME = "shortParQuantity"
    
    #: Number: Aggregate reported share volume of executed short sale exempt
    #: trades during regular trading hours
    SHORT_EXEMPT_VOLUME = "shortExemptParQuantity"
    
    #: Number: Aggregate reported share volume of all executed trades during
    #: regular trading hours
    TOTAL_VOLUME = "totalParQuantity"
    
    #: String: Market Code. Possible values:
    #:
    #: - ``N`` : NYSE TRF
    #: - ``Q`` : NASDAQ TRF Carteret
    #: - ``B`` : NASDAQ TRF Chicago
    #: - ``D`` : Alternative Display Facility
    MARKET_CODE = "marketCode"
    
    #: String: Reporting Facility Identifier. Possible values:
    #:
    #: - ``NYTRF`` : NYSE TRF
    #: - ``NQTRF`` : NASDAQ TRF Carteret
    #: - ``NCTRF`` : NASDAQ TRF Chicago
    #: - ``ADF`` : Alternative Display Facility
    REPORTING_FACILITY_CODE = "reportingFacilityCode"


class ThresholdList(Enum):
    """Fields returned by :py:meth:`BaseClient.get_threshold_list`"""
    
    #: Date: **Partition Field**. Trade Date.
    #: Format: yyyy-MM-dd
    TRADE_DATE = "tradeDate"
    
    #: String: Issue Symbol identifier
    SYMBOL = "issueSymbolIdentifier"
    
    #: String: Issue Name
    ISSUE_NAME = "issueName"
    
    #: String: Indicates whether the issue is OTC Bulletin Board (U) or
    #: non-Bulletin Board (u)
    MARKET_CLASS_CODE = "marketClassCode"
    
    #: String: Indicates  whether the issue is a threshold security pursuant to
    #: Regulation SHO (R) or FINRA Rule 4320 (NR)
    THRESHOLD_LIST_FLAG = "thresholdListFlag"
    
    #: String: Describes the code that indicates whether the issue is
    #: OTC Bulletin Board (U) or non-Bulletin Board (u)
    MARKET_CATEGORY_DESCRIPTION = "marketCategoryDescription"
    
    #: String: Subject to the requirements of SEC Rule 203 of Regulation SHO
    #: where there is an aggregate fail to deliver position for five
    #: consecutive settlement days at a registered clearing agency
    #: totaling 10,000 shares or more and equal to at least 0.5% of the
    #: issuer's total shares outstanding. When this occurs, the issue
    #: becomes subject to mandatory close-out requirements outlined in
    #: the SEC's Regulation SHO.
    REG_SHO_THRESHOLD_FLAG = "regShoThresholdFlag"
    
    #: String: Subject to the requirements of FINRA Rule 4320 where, for five
    #: consecutive settlement days, there are aggregate fails to
    #: deliver at a registered clearing agency of 10,000 shares or more
    #: and the reported last sale during normal market hours would
    #: value the aggregate fail to deliver position at $50,000 or more.
    #: When this occurs, the issue becomes subject to mandatory
    #: close-out requirements outlined in NASD Rule 3210.
    RULE_4320_FLAG = "rule4320Flag"


class WeeklySummary(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_weekly_summary` and
    :py:meth:`BaseClient.get_weekly_summary_historic`
    """
    
    #: Date: **Primary Partition Field**. The first business day of the week
    #: (Monday).
    #: Format: yyyy-MM-dd
    WEEK_START_DATE = "weekStartDate"
    
    #: String: **Secondary Partition Field**. Tier Identifier. Possible values:
    #:
    #: - ``T1`` : Securities included in the S&P 500, Russell 1000 and selected
    #:   exchange-traded products
    #: - ``T2`` : All other NMS stocks
    #: - ``OTCE`` : Over-the-Counter equity securities
    #: - ``NMS`` : National Market System (undocumented)
    #: - ``NA`` : Not applicable (undocumented)
    TIER_IDENTIFIER = "tierIdentifier"
    
    #: String: Security Symbol.
    #: Assigned by the NASDAQ listing market and ACT Symbol for Other
    #: Exchange Listed (NMS stocks), or by FINRA (OTCE securities).
    #: Suffix is separated from root symbol with a special character.
    SYMBOL = "issueSymbolIdentifier"
    
    #: String: Company name associated with the Symbol
    ISSUE_NAME = "issueName"
    
    #: Number: Firm CRD Number
    FIRM_CRD_NUMBER = "firmCRDNumber"
    
    #: String: ATS/OTC identifier
    MPID = "MPID"
    
    #: String: Company name of the ATS/OTC or De Minimis Firm
    MARKET_PARTICIPANT_NAME = "marketParticipantName"
    
    #: String: Tier Description. Possible values:
    #:
    #: - ``NMS Tier 1`` : Securities included in the S&P 500, Russell 1000 and
    #:   selected exchange-traded products
    #: - ``NMS Tier 2`` : All other NMS stocks
    #: - ``OTCE`` : Over-the-Counter equity securities
    #: - ``OTC`` : (typo? undocumented)
    #: - ``Not Applicable`` : No tier identifier available (undocumented)
    TIER_DESCRIPTION = "tierDescription"
    
    #: Date: Report Start Date (Monday).
    #: Format: yyyy-MM-dd
    SUMMARY_START_DATE = "summaryStartDate"
    
    #: Number: Aggregate weekly total number of trades reported by each ATS for
    #: the Symbol
    TOTAL_TRADES = "totalWeeklyTradeCount"
    
    #: Number: Aggregate weekly total number of shares reported by each ATS for
    #: the Symbol
    TOTAL_VOLUME = "totalWeeklyShareQuantity"
    
    #: String: Product Type
    PRODUCT_TYPE_CODE = "productTypeCode"
    
    #: String: Report Type Identifier. Possible values:
    #:
    #: - ``OTC_W_FIRM`` : OTC Weekly Firm
    #: - ``OTC_W_SMBL`` : OTC Weekly Symbol
    #: - ``OTC_W_SMBL_FIRM`` : OTC Weekly Symbol Firm
    #: - ``OTC_W_VOL_STATS`` : OTC Volume Statistics
    #: - ``ATS_W_FIRM`` : ATS Weekly Firm
    #: - ``ATS_W_SMBL`` : ATS Weekly Symbol
    #: - ``ATS_W_SMBL_FIRM`` : ATS Weekly Symbol Firm
    #: - ``ATS_W_VOL_STATS`` : ATS Volume Statistics
    SUMMARY_TYPE_CODE = "summaryTypeCode"
    
    #: Date: Most recent date on which total trades was updated based on data
    #: received from each ATS/OTC.
    #: Format: yyyy-MM-dd
    LAST_UPDATE_DATE = "lastUpdateDate"
    
    #: Date: The initial publish date is the first Monday or next business day
    #: after the reporting delay based on NMS Tier 1 (two week delay),
    #: NMS Tier 2 (four week delay) and OTC securities (four week delay).
    #: Format: yyyy-MM-dd
    INITIAL_PUBLISHED_DATE = "initialPublishedDate"
    
    #: Date: This date represents the last time a firm sent an update to any
    #: underlying data that contributes to the aggregate count.
    #: Format: yyyy-MM-dd
    LAST_REPORTED_DATE = "lastReportedDate"
    
    #: Number: Calculated Total Notional value of equity trades.
    #: **NOTE:** Field is not in mock dataset!
    TOTAL_NOTIONAL_SUM = "totalNotionalSum"
    
    #: Date: The date used to query the historic dataset and calculate the
    #: corresponding :py:attr:`WEEK_START_DATE`.
    #: **NOTE:** Field is only available in historic datasets when requesting
    #: data using ``historical_week``.
    #: Format: yyyy-MM-dd
    HISTORICAL_WEEK = "historicalweek"
    
    #: Date: The month start date (first day of the month) used to query the
    #: historic dataset.
    #: **NOTE:** Field is only available in historic datasets when requesting
    #: data with ``historical_month``.
    #: Format: yyyy-MM-dd
    HISTORICAL_MONTH = "historicalmonth"


class MonthlySummary(Enum):
    """Fields returned by :py:meth:`BaseClient.get_monthly_summary`"""
    
    #: Date: **Primary Partition Field**. The first day of the month.
    #: Format: yyyy-MM-dd
    MONTH_START_DATE = "monthStartDate"
    
    #: String: **Secondary Partition Field**. Tier Identifier. Possible values:
    #:
    #: - ``NMS`` : National Market System stocks
    #: - ``OTCE`` : All Over-the-Counter equity securities
    TIER_IDENTIFIER = "tierIdentifier"
    
    #: String: Security Symbol.
    #: Assigned by the NASDAQ listing market and ACT Symbol for Other
    #: Exchange Listed (NMS stocks), or by FINRA (OTCE securities).
    #: Suffix is separated from root symbol with a special character.
    SYMBOL = "issueSymbolIdentifier"
    
    #: String: Company name associated with the Symbol
    ISSUE_NAME = "issueName"
    
    #: Number: Firm CRD Number
    FIRM_CRD_NUMBER = "firmCRDNumber"
    
    #: String: Company name of the OTC or De Minimis Firm
    MARKET_PARTICIPANT_NAME = "marketParticipantName"
    
    #: Date: Start Date (first of the month) of the summary data.
    #: Format: yyyy-MM-dd
    SUMMARY_START_DATE = "summaryStartDate"
    
    #: Number: Aggregate monthly total number of OTC (non-ATS) trades reported
    #: by each firm for the symbol
    TOTAL_TRADES = "totalMonthlyTradeCount"
    
    #: Number: Aggregate monthly total number of OTC (non-ATS) shares reported
    #: by each firm for the symbol
    TOTAL_VOLUME = "totalMonthlyShareQuantity"
    
    #: String: Product Type
    PRODUCT_TYPE_CODE = "productTypeCode"
    
    #: String: Summary Type Identifier. Possible values:
    #:
    #: - ``OTC_M_FIRM`` : OTC Monthly Firm
    #: - ``OTC_M_SMBL`` : OTC Monthly Symbol
    #: - ``OTC_M_SMBL_FIRM`` : OTC Monthly Symbol Firm
    #: - ``OTC_M_VOL_STATS`` : OTC Monthly Volume Stats
    SUMMARY_TYPE_CODE = "summaryTypeCode"
    
    #: Date: Most recent date on which total OTC (non-ATS) trades was updated
    #: based on data received from each firm.
    #: Format: yyyy-MM-dd
    LAST_UPDATE_DATE = "lastUpdateDate"
    
    #: Date: This date represents the date of the first publication of the
    #: data, the first Monday or next business day of the following month.
    #: Format: yyyy-MM-dd
    INITIAL_PUBLISHED_DATE = "initialPublishedDate"
    
    #: Date: This date represents the last time a firm sent an update to any
    #: underlying data that contributes to the aggregate count.
    #: Format: yyyy-MM-dd
    LAST_REPORTED_DATE = "lastReportedDate"
    
    #: Number: Calculated Total Notional value of equity trades.
    #: **NOTE:** Field is not in mock dataset!
    TOTAL_NOTIONAL_SUM = "totalNotionalSum"


class OTCDailyList(Enum):
    """Fields returned by :py:meth:`BaseClient.get_otc_daily_list`"""
    
    #: Date: **Partition Field**. Calendar day of intra-day symbol
    #: modification.
    #: Format: yyyy-MM-dd
    CALENDAR_DAY = "calendarDay"
    
    #: String: Old OATS Reportable Flag
    OLD_OATS_REPORTABLE_FLAG = "oldOATSReportableFlag"
    
    #: String: New Symbol
    NEW_SYMBOL_CODE = "newSymbolCode"
    
    #: Number: ADR Withholding Tax
    ADR_WITHOLDING_TAX_PERCENTAGE = "ADRWitholdingTaxPercentage"
    
    #: String: Old ADR Ordinary Share Ratio
    OLD_ADR_ORDINARY_SHARE_RATE = "oldADROrdinaryShareRate"
    
    #: String: New Security Descriptiion
    NEW_SECURITY_DESCRIPTION = "newSecurityDescription"
    
    #: String: Subject to Corp Action
    SUBJECT_CORPORATE_ACTION_CODE = "subjectCorporateActionCode"
    
    #: String: Old Reg Fee Flag
    OLD_REG_FEE_FLAG = "oldRegFeeFlag"
    
    #: String: Daily List Reason Description
    DAILY_LIST_REASON_DESCRIPTION = "dailyListReasonDescription"
    
    #: String: Change Round Lot Quantity Flag
    CHANGE_ROUND_LOT_QUANTITY_FLAG = "changeRoundLotQuantityFlag"
    
    #: String: Bankruptcy Flag
    BANKRUPTCY_FLAG = "bankruptcyFlag"
    
    #: String: Change Security Description Flag
    CHANGE_SECURITY_DESCRIPTION_FLAG = "changeSecurityDescriptionFlag"
    
    #: String: Change OATS Reportable Flag
    CHANGE_OATS_REPORTABLE_FLAG = "changeOATSReportableFlag"
    
    #: Number: Stock Percentage
    STOCK_PERCENTAGE = "stockPercentage"
    
    #: String: New OATS Reportable Flag
    NEW_OATS_REPORTABLE_FLAG = "newOATSReportableFlag"
    
    #: String: New Financial Status Code
    NEW_FINANCIAL_STATUS_CODE = "newFinancialStatusCode"
    
    #: String: Qualified Dividend Description
    QUALIFIED_DIVIDEND_DESCRIPTION = "qualifiedDividendDescription"
    
    #: String: New Class Value
    NEW_CLASS_TEXT = "newClassText"
    
    #: String: Old Security Description
    OLD_SECURITY_DESCRIPTION = "oldSecurityDescription"
    
    #: String: Offering Type Description
    OFFERING_TYPE_DESCRIPTION = "offeringTypeDescription"
    
    #: String: Old Class Text
    OLD_CLASS_TEXT = "oldClassText"
    
    #: String: Dividend Type
    DIVIDEND_TYPE_DESCRIPTION = "dividendTypeDescription"
    
    #: Number: ADR Net Rate
    ADR_NET_RATE = "ADRNetRate"
    
    #: String: New Reg Fee Flag
    NEW_REG_FEE_FLAG = "newRegFeeFlag"
    
    #: String: Daily List Event Type
    DAILY_LIST_EVENT_CODE = "dailyListEventCode"
    
    #: Number: ADR Dividend Fee
    ADR_FEE_AMOUNT = "ADRFeeAmount"
    
    #: Number: OTC Daily List ID
    OTC_DAILY_LIST_ID = "OTCDailyListID"
    
    #: String: Payment Method
    PAYMENT_METHOD_CODE = "paymentMethodCode"
    
    #: Number: ADR Gross Rate
    ADR_GROSS_RATE = "ADRGrossRate"
    
    #: String: New Market Category Code
    NEW_MARKET_CATEGORY_CODE = "newMarketCategoryCode"
    
    #: Date: Old Maturity Expiration Date.
    #: Format: yyyy-MM-dd
    OLD_MATURITY_EXPIRATION_DATE = "oldMaturityExpirationDate"
    
    #: Datetime: Daily List Date/Time.
    #: Format: yyyy-MM-dd HH:mm:ss.SSS
    DAILY_LIST_DATETIME = "dailyListDatetime"
    
    #: String: Old Market Category Code
    OLD_MARKET_CATEGORY_CODE = "oldMarketCategoryCode"
    
    #: String: Change Symbol Flag
    CHANGE_SYMBOL_FLAG = "changeSymbolFlag"
    
    #: Number: Old Round Lot Quantity
    OLD_ROUND_LOT_QUANTITY = "oldRoundLotQuantity"
    
    #: String: Change Reg Fee Flag
    CHANGE_REG_FEE_FLAG = "changeRegFeeFlag"
    
    #: String: Comment
    COMMENT_TEXT = "commentText"
    
    #: Number: ADR Tax Relief Fee
    ADR_TAX_RELIEF_AMOUNT = "ADRTaxReliefAmount"
    
    #: String: Security Deletions
    SECURITY_DELETE_FLAG = "securityDeleteFlag"
    
    #: Number: ADR Issauance Fee
    ADR_ISSUANCE_FEE_AMOUNT = "ADRIssuanceFeeAmount"
    
    #: Date: Record Date.
    #: Format: yyyy-MM-dd
    RECORD_DATE = "recordDate"
    
    #: String: Dividend Type
    DIVIDEND_TYPE_CODE = "dividendTypeCode"
    
    #: Datetime: Effective/Ex Date/Time.
    #: Format: yyyy-MM-dd HH:mm:ss.SSS
    EX_DATETIME = "exDate"
    
    #: String: Change Finanical Status Flag
    CHANGE_FINANCIAL_STATUS_FLAG = "changeFinancialStatusFlag"
    
    #: String: Dividend ADR/GDR Indicator
    DIVIDEND_ADR_FLAG = "dividendADRFlag"
    
    #: Number: Dividend Master ID
    DIVIDEND_MASTER_ID = "dividendMasterID"
    
    #: Date: Payment Date.
    #: Format: yyyy-MM-dd
    PAYMENT_DATE = "paymentDate"
    
    #: Date: Declaration Date.
    #: Format: yyyy-MM-dd
    DECLARATION_DATE = "declarationDate"
    
    #: String: Old Symbol
    OLD_SYMBOL_CODE = "oldSymbolCode"
    
    #: String: Change OTCBB Quote Flag
    CHANGE_OTCBB_QUOTE_FLAG = "changeOTCBBQuoteFlag"
    
    #: Number: New Round Lot Quantity
    NEW_ROUND_LOT_QUANTITY = "newRoundLotQuantity"
    
    #: String: ADR Ratio Current Value
    NEW_ADR_ORDNY_SHARE_RATE = "newADROrdnyShareRate"
    
    #: String: Old Finanical Status Code
    OLD_FINANCIAL_STATUS_CODE = "oldFinancialStatusCode"
    
    #: String: Change Security Attribute Flag
    CHANGE_SECURITY_ATTRIBUTE_FLAG = "changeSecurityAttributeFlag"
    
    #: String: Forward Split Ratio
    FORWARD_SPLIT_RATE = "forwardSplitRate"
    
    #: String: Reverse Split Ratio
    REVERSE_SPLIT_RATE = "reverseSplitRate"
    
    #: Date: New Maturity Expiration Date.
    #: Format: yyyy-MM-dd
    NEW_MATURITY_EXPIRATION_DATE = "newMaturityExpirationDate"
    
    #: String: Cash Amount
    CASH_AMOUNT_TEXT = "cashAmountText"
    
    #: String: Security Additions
    SECURITY_ADD_FLAG = "securityAddFlag"
    
    #: String: Dividend Non ADR/GDR Indicator
    DIVIDEND_NON_ADR_FLAG = "dividendNonADRFlag"


##########################################################################
# FIXED INCOME GROUP

class AgencyTBAPricing(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_agency_tba_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The settlement period code for the TBA security
    SETTLEMENT_CODE = "settlementCode"
    
    #: String: The agency code identifying the issuing agency (e.g., GNMA,
    #: FNMA, FHLMC)
    AGENCY_CODE = "agencyCode"
    
    #: String: The coupon rate code for the TBA security
    COUPON_RATE_CODE = "couponRateCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class AgencyCMOPricing(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_agency_cmo_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The agency code identifying the issuing agency (e.g., GNMA,
    #: FNMA, FHLMC)
    AGENCY_CODE = "agencyCode"
    
    #: String: The vintage year code for the CMO tranche
    VINTAGE_CODE = "vintageCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: String: The pricing sub-category code providing additional
    #: classification
    SUB_CATEGORY_CODE = "subCategoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class AgencyDebtMarketBreadth(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_agency_debt_market_breadth`
    """
    
    #: Date: **Partition Field**. Trade date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: String: Category of the product
    PRODUCT_CATEGORY = "productCategory"
    
    #: Number: Total number of trades
    TOTAL_TRADES = "totalTrades"
    
    #: Number: Advances
    ADVANCES = "advances"
    
    #: Number: Declines
    DECLINES = "declines"
    
    #: Number: Unchanged
    UNCHANGED = "unchanged"
    
    #: Number: 52 weeks high
    HIGH_52_WEEK = "fiftyTwoWeekHigh"
    
    #: Number: 52 weeks low
    LOW_52_WEEK = "fiftyTwoWeekLow"
    
    #: Number: Total volume count
    TOTAL_VOLUME = "totalVolume"


class AgencyDebtMarketSentiment(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_agency_debt_market_sentiment`
    """
    
    #: Date: **Partition Field**. Trade date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: String: Trade Type
    TRADE_TYPE = "tradeType"
    
    #: String: Category of the product
    PRODUCT_CATEGORY = "productCategory"
    
    #: Number: Total count of transactions
    TOTAL_TRANSACTIONS = "totalTransactions"
    
    #: Number: Total number of trades
    TOTAL_TRADES = "totalTrades"
    
    #: Number: Total volume count
    TOTAL_VOLUME = "totalVolume"


class AgencyMBSTradingActivity(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_agency_mbs_trading_activity`
    """
    
    #: Date: The report date for the trading activity data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The agency code identifying the issuing agency (e.g., GNMA,
    #: FNMA, FHLMC)
    AGENCY_CODE = "agencyCode"
    
    #: String: The trading activity category code
    CATEGORY_CODE = "categoryCode"
    
    #: String: The MBS product type code
    PRODUCT_CODE = "productCode"
    
    #: String: The MBS sub-product type code providing further classification
    SUB_PRODUCT_CODE = "subProductCode"
    
    #: Number: The numeric value for the given trading activity metric
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class AgencyMBSARMHybridPricing(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_agency_mbs_arm_hybrid_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The agency code identifying the issuing agency (e.g., GNMA,
    #: FNMA, FHLMC)
    AGENCY_CODE = "agencyCode"
    
    #: String: The fixed rate period code for the adjustable rate MBS security
    FIXED_RATE_PERIOD_CODE = "fixedRatePeriodCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class AgencyMBSPricing(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_agency_mbs_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The agency code identifying the issuing agency (e.g., GNMA,
    #: FNMA, FHLMC)
    AGENCY_CODE = "agencyCode"
    
    #: String: The coupon rate code for the MBS security
    COUPON_RATE_CODE = "couponRateCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class CollateralizedObligationsPricing(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_collateralized_obligations_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The CBO/CDO/CLO product type code (e.g., CBO, CDO, CLO)
    PRODUCT_CODE = "productCode"
    
    #: String: The vintage year code for the tranche
    VINTAGE_CODE = "vintageCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: String: The pricing sub-category code providing additional
    #: classification
    SUB_CATEGORY_CODE = "subCategoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class Corporate144ADebtMarketBreadth(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_corporate_144a_debt_market_breadth`
    """
    
    #: Date: **Partition Field**. Trade date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: String: Category of the product
    PRODUCT_CATEGORY = "productCategory"
    
    #: Number: Total number of trades
    TOTAL_TRADES = "totalTrades"
    
    #: Number: Advances
    ADVANCES = "advances"
    
    #: Number: Declines
    DECLINES = "declines"
    
    #: Number: Unchanged
    UNCHANGED = "unchanged"
    
    #: Number: 52 weeks high
    HIGH_52_WEEK = "fiftyTwoWeekHigh"
    
    #: Number: 52 weeks low
    LOW_52_WEEK = "fiftyTwoWeekLow"
    
    #: Number: Total volume count
    TOTAL_VOLUME = "totalVolume"


class Corporate144ADebtMarketSentiment(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_corporate_144a_debt_market_sentiment`
    """
    
    #: Date: **Partition Field**. Trade date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: String: Trade Type
    TRADE_TYPE = "tradeType"
    
    #: String: Category of the product
    PRODUCT_CATEGORY = "productCategory"
    
    #: Number: Total count of transactions
    TOTAL_TRANSACTIONS = "totalTransactions"
    
    #: Number: Total number of trades
    TOTAL_TRADES = "totalTrades"
    
    #: Number: Total volume count
    TOTAL_VOLUME = "totalVolume"


class CorporateAndAgencyCappedVolume(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_corporate_and_agency_capped_volume`
    """
    
    #: Date: **Partition Field**. Trade date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: Number: Month of the trade date
    TRADE_MONTH = "tradeMonth"
    
    #: Number: Year of the trade date
    TRADE_YEAR = "tradeYear"
    
    #: String: Grade code – Investment Grade, High Yield, Agency (IG, HY, AGCY)
    GRADE_CODE = "gradeCode"
    
    #: String: Flag to indicate if security is 144A (Y/N)
    FLAG_144A = "144AFlag"
    
    #: Number: Total trade count
    TOTAL_TRADES = "totalTradeCount"
    
    #: Number: Total share volume quantity
    TOTAL_VOLUME = "totalVolumeQuantity"
    
    #: Number: Volume less than 5 million
    VOLUME_LESS_THAN_5_MILLION = "parLessThan5MillionQuantity"
    
    #: Number: Volume greater than 5 million and less than 10 million
    VOLUME_BETWEEN_5_AND_10_MILLION = \
        "parGreaterThan5MillionLessThan10MillionQuantity"
    
    #: Number: Volume greater than 10 million and less than 25 million
    VOLUME_BETWEEN_10_AND_25_MILLION = \
        "parGreaterThan10MillionLessThan25MillionQuantity"
    
    #: Number: Volume greater than 25 million
    VOLUME_GREATER_THAN_25_MILLION = "parGreaterThan25MillionQuantity"
    
    #: Number: Trade count less then 5 million
    TRADES_LESS_THAN_5_MILLION = "tradeLessThan5MillionCount"
    
    #: Number: Trade count greater than 5 million and less than 10 million
    TRADES_BETWEEN_5_AND_10_MILLION = \
        "tradeGreaterThan5MillionLessThan10MillionCount"
    
    #: Number: Trade count greater than 10 million and less than 25 million
    TRADES_BETWEEN_10_AND_25_MILLION = \
        "tradeGreaterThan10MillionLessThan25MillionCount"
    
    #: Number: Trade count greater than 25 millions
    TRADES_GREATER_THAN_25_MILLION = "tradeGreaterThan25MillionCount"
    
    #: Number: Volume with maturity date less than 5yrs
    VOLUME_MATURITY_LESS_THAN_5_YEARS = "parMaturityLessThan5YearsQuantity"
    
    #: Number: Trade Count with maturity date less than 5yrs
    TRADES_MATURITY_LESS_THAN_5_YEARS = "tradeMaturityLessThan5YearsCount"
    
    #: Number: Volume with maturity date greater than 5yrs less than 10yrs
    VOLUME_MATURITY_BETWEEN_5_AND_10_YEARS = \
        "parMaturityGreaterThan5YearsLessThan10YearsQuantity"
    
    #: Number: Trade Count with maturity date greater than 5yrs less than 10yrs
    TRADES_MATURITY_BETWEEN_5_AND_10_YEARS = \
        "tradeMaturityGreaterThan5YearsLessThan10YearsCount"
    
    #: Number: Volume with maturity date greater than 10yrs less than 25yrs
    VOLUME_MATURITY_BETWEEN_10_AND_25_YEARS = \
        "parMaturityGreaterThan10YearsLessThan25YearsQuantity"
    
    #: Number: Trade Count with maturity date greater than 10yrs less than
    #: 25yrs
    TRADES_MATURITY_BETWEEN_10_AND_25_YEARS = \
        "tradeMaturityGreaterThan10YearsLessThan25YearsCount"
    
    #: Number: Volume with maturity date greater than 25yrs
    VOLUME_MATURITY_GREATER_THAN_25_YEARS = \
        "parMaturityGreaterThan25YearsQuantity"
    
    #: Number: Trade Count with maturity date greater than 25yrs
    TRADES_MATURITY_GREATER_THAN_25_YEARS = \
        "tradeMaturityGreaterThan25YearsCount"
    
    #: Number: Customer Buy Volume quantity with maturity date less than 5yrs
    CUSTOMER_BUY_VOLUME_MATURITY_LESS_THAN_5_YEARS = \
        "customerBuyParLessThan5YearsQuantity"
    
    #: Number: Customer Buy Trade Count with maturity date less than 5yrs
    CUSTOMER_BUY_TRADES_MATURITY_LESS_THAN_5_YEARS = \
        "customerBuyTradeMaturityLessThan5YearsCount"
    
    #: Number: Customer Buy Volume quantity with maturity date
    #: greater than 5yrs less than 10yrs
    CUSTOMER_BUY_VOLUME_MATURITY_BETWEEN_5_AND_10_YEARS = \
        "customerBuyParGreaterThan5YearsLessThan10YearsQuantity"
    
    #: Number: Customer Buy Trade Count with maturity date
    #: greater than 5yrs less than 10yrs
    CUSTOMER_BUY_TRADES_MATURITY_BETWEEN_5_AND_10_YEARS = \
        "customerBuyTradeMaturityGreaterThan5YearsLessThan10YearsCount"
    
    #: Number: Customer Buy Volume quantity with maturity date
    #: greater than 10yrs less than 25yrs
    CUSTOMER_BUY_VOLUME_MATURITY_BETWEEN_10_AND_25_YEARS = \
        "customerBuyParGreaterThan10YearsLessThan25YearsQuantity"
    
    #: Number: Customer Buy Trade Count  with maturity date
    #: greater than 10yrs less than 25yrs
    CUSTOMER_BUY_TRADES_MATURITY_BETWEEN_10_AND_25_YEARS = \
        "customerBuyTradeMaturityGreaterThan10YearsLessThan25YearsCount"
    
    #: Number: Customer Buy Volume quantity with maturity date
    #: greater than 25yrs
    CUSTOMER_BUY_VOLUME_MATURITY_GREATER_THAN_25_YEARS = \
        "customerBuyParGreaterThan25YearsQuantity"
    
    #: Number: Customer Buy Trade Count with maturity date greater than 25yrs
    CUSTOMER_BUY_TRADES_MATURITY_GREATER_THAN_25_YEARS = \
        "customerBuyTradeMaturityGreaterThan25YearsCount"
    
    #: Number: Customer Sell Volume quantity with maturity date less than 5yrs
    CUSTOMER_SELL_VOLUME_MATURITY_LESS_THAN_5_YEARS = \
        "customerSellParLessThan5YearsQuantity"
    
    #: Number: Customer Sell Trade Count with maturity date less than 5yrs
    CUSTOMER_SELL_TRADES_MATURITY_LESS_THAN_5_YEARS = \
        "customerSellTradeMaturityLessThan5YearsCount"
    
    #: Number: Customer Sell Volume quantity with maturity date
    #: greater than 5yrs less than 10yrs
    CUSTOMER_SELL_VOLUME_MATURITY_BETWEEN_5_AND_10_YEARS = \
        "customerSellParGreaterThan5YearsLessThan10YearsQuantity"
    
    #: Number: Customer Sell Trade Count with maturity date
    #: greater than 5yrs less than 10yrs
    CUSTOMER_SELL_TRADES_MATURITY_BETWEEN_5_AND_10_YEARS = \
        "customerSellTradeMaturityGreaterThan5YearsLessThan10YearsCount"
    
    #: Number: Customer Sell Volume quantity with maturity date
    #: greater than 10yrs less than 25yrs
    CUSTOMER_SELL_VOLUME_MATURITY_BETWEEN_10_AND_25_YEARS = \
        "customerSellParGreaterThan10YearsLessThan25YearsQuantity"
    
    #: Number: Customer Sell Trade Count  with maturity date
    #: greater than 10yrs less than 25yrs
    CUSTOMER_SELL_TRADES_MATURITY_BETWEEN_10_AND_25_YEARS = \
        "customerSellTradeMaturityGreaterThan10YearsLessThan25YearsCount"
    
    #: Number: Customer Sell Volume quantity with maturity date
    #: greater than 25yrs
    CUSTOMER_SELL_VOLUME_MATURITY_GREATER_THAN_25_YEARS = \
        "customerSellParGreaterThan25YearsQuantity"
    
    #: Number: Customer Sell Trade Count with maturity date greater than 25yrs
    CUSTOMER_SELL_TRADES_MATURITY_GREATER_THAN_25_YEARS = \
        "customerSellTradeMaturityGreaterThan25YearsCount"
    
    #: Number: Interdealer Volume quantity with maturity date less than 5yrs
    INTERDEALER_VOLUME_MATURITY_LESS_THAN_5_YEARS = \
        "interdealerParLessThan5yearsQuantity"
    
    #: Number: Interdealer Trade Count with maturity date less than 5yrs
    INTERDEALER_TRADES_MATURITY_LESS_THAN_5_YEARS = \
        "interdealerMaturityTradeLessThan5yearsCount"
    
    #: Number: Interdealer Volume quantity with maturity date
    #: greater than 5yrs less than 10yrs
    INTERDEALER_VOLUME_MATURITY_BETWEEN_5_AND_10_YEARS = \
        "interdealerParGreaterThan5yearsLessThan10YearsQuantity"
    
    #: Number: Interdealer Trade Count with maturity date
    #: greater than 5yrs less than 10yrs
    INTERDEALER_TRADES_MATURITY_BETWEEN_5_AND_10_YEARS = \
        "interdealerTradeMaturityGreaterThan5yearsLessThan10YearsCount"
    
    #: Number: Interdealer Volume quantity with maturity date
    #: greater than 10yrs less than 25yrs
    INTERDEALER_VOLUME_MATURITY_BETWEEN_10_AND_25_YEARS = \
        "interdealerParGreaterThan10yCountearsLessThan25YearsQuantity"
    
    #: Number: Interdealer Trade Count with maturity date
    #: greater than 10yrs less than 25yrs
    INTERDEALER_TRADES_MATURITY_BETWEEN_10_AND_25_YEARS = \
        "interdealerTradeMaturityGreaterThan10yearsLessThan25YearsCount"
    
    #: Number: Interdealer Volume quantity with maturity date greater than
    #: 25yrs
    INTERDEALER_VOLUME_MATURITY_GREATER_THAN_25_YEARS = \
        "interdealerParGreaterThan25YearsQuantity"
    
    #: Number: Interdealer Trade Count with maturity date greater than 25yrs
    INTERDEALER_TRADES_MATURITY_GREATER_THAN_25_YEARS = \
        "interdealerTradeMaturityGreaterThan25YearsCount"


class CorporateDebtMarketBreadth(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_corporate_debt_market_breadth`
    """
    
    #: Date: **Partition Field**. Trade date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: String: Category of the product
    PRODUCT_CATEGORY = "productCategory"
    
    #: Number: Total number of trades
    TOTAL_TRADES = "totalTrades"
    
    #: Number: Advances
    ADVANCES = "advances"
    
    #: Number: Declines
    DECLINES = "declines"
    
    #: Number: Unchanged
    UNCHANGED = "unchanged"
    
    #: Number: 52 weeks high
    HIGH_52_WEEK = "fiftyTwoWeekHigh"
    
    #: Number: 52 weeks low
    LOW_52_WEEK = "fiftyTwoWeekLow"
    
    #: Number: Total volume count
    TOTAL_VOLUME = "totalVolume"


class CorporateDebtMarketSentiment(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_corporate_debt_market_sentiment`
    """
    
    #: Date: **Partition Field**. Trade date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: String: Trade Type
    TRADE_TYPE = "tradeType"
    
    #: String: Category of the product
    PRODUCT_CATEGORY = "productCategory"
    
    #: Number: Total count of transactions
    TOTAL_TRANSACTIONS = "totalTransactions"
    
    #: Number: Total number of trades
    TOTAL_TRADES = "totalTrades"
    
    #: Number: Total volume count
    TOTAL_VOLUME = "totalVolume"


class DailyCMBSPricing(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_daily_cmbs_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The CMBS product type code
    PRODUCT_CODE = "productCode"
    
    #: String: The vintage year code for the CMBS tranche
    VINTAGE_CODE = "vintageCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: String: The pricing sub-category code providing additional
    #: classification
    SUB_CATEGORY_CODE = "subCategoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class NonAgencyCMOABSPricing(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_non_agency_cmo_abs_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The credit grade code (e.g., IG, NIG)
    GRADE_CODE = "gradeCode"
    
    #: String: The product type code for the non-agency CMO
    PRODUCT_CODE = "productCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: String: The pricing sub-category code providing additional
    #: classification
    SUB_CATEGORY_CODE = "subCategoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class NonAgencyCMOPricing(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_non_agency_cmo_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The credit grade code (e.g., IG, NIG)
    GRADE_CODE = "gradeCode"
    
    #: String: The vintage year code for the CMO tranche
    VINTAGE_CODE = "vintageCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: String: The pricing sub-category code providing additional
    #: classification
    SUB_CATEGORY_CODE = "subCategoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class SecuritizedProductsCappedVolume(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_securitized_products_capped_volume`
    """
    
    #: Date: **Partition Field**. Trade date.
    #: Format: yyyy-MM-dd
    TRADE_REPORT_DATE = "tradeReportDate"
    
    #: Number: Month of the trade date
    TRADE_MONTH = "tradeMonth"
    
    #: Number: Year of the trade date
    TRADE_YEAR = "tradeYear"
    
    #: String: Product Type
    PRODUCT_TYPE = "productType"
    
    #: String: Security sub type
    SECURITY_SUBTYPE = "securitySubtype"
    
    #: Number: Average Transaction Count
    AVERAGE_TRANSACTION_COUNT = "averageTransactionCount"


class SecuritizedProductsErrata(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_securitized_products_errata`
    """
    
    #: Date: The report date for the errata data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: Date: The original trade date associated with the errata correction.
    #: Format: yyyy-MM-dd
    TRADE_DATE = "tradeDate"
    
    #: Date: The date the correction was made.
    #: Format: yyyy-MM-dd
    CORRECTION_DATE = "correctionDate"
    
    #: String: The asset class code for the errata entry
    ASSET_CODE = "assetCode"
    
    #: String: The sub-asset class code for the errata entry
    SUB_ASSET_CODE = "subAssetCode"
    
    #: String: The descriptive note explaining the errata correction
    NOTE_TEXT = "noteText"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class SecuritizedProductsTradingActivity(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_securitized_products_trading_activity`
    """
    
    #: Date: The report date for the trading activity data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The credit grade code (e.g., IG, NIG)
    GRADE_CODE = "gradeCode"
    
    #: String: The trading activity category code
    CATEGORY_CODE = "categoryCode"
    
    #: String: The product type code for the trading activity
    PRODUCT_CODE = "productCode"
    
    #: Number: The numeric value for the given trading activity metric
    VALUE_AMOUNT = "valueAmount"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


class TreasuryDailyAggregates(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_treasury_daily_aggregates`
    """
    
    #: Date: **Partition Field**. Date on which the security was traded.
    #: Format: yyyy-MM-dd
    TRADE_DATE = "tradeDate"
    
    #: String: Category of the Treasury product
    PRODUCT_CATEGORY = "productCategory"
    
    #: String: Range of years to maturity
    YEARS_TO_MATURITY = "yearsToMaturity"
    
    #: String: Run Code
    BENCHMARK = "benchmark"
    
    #: Number: Count of securities for ATS-Interdealer
    ATS_INTERDEALER_TRADES = "atsInterdealerCount"
    
    #: Number: Volume in Dollars for ATS-Interdealer
    ATS_INTERDEALER_VOLUME = "atsInterdealerVolume"
    
    #: Number: Count of securities for Dealer-Customer
    DEALER_CUSTOMER_TRADES = "dealerCustomerCount"
    
    #: Number: Volume in Dollars for Dealer-Customer
    DEALER_CUSTOMER_VOLUME = "dealerCustomerVolume"
    
    #: Number: The volume weighted average price for the day
    VOLUME_WEIGHTED_AVERAGE_PRICE = "volumeWeightedAveragePrice"


class TreasuryMonthlyAggregates(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_treasury_monthly_aggregates`
    """
    
    #: Date: **Partition Field**. The first day for the month for the data
    #: contained in this report.
    #: Format: yyyy-MM-dd
    BEGINNING_OF_MONTH_DATE = "beginningOfTheMonthDate"
    
    #: String: Category of the Treasury product
    PRODUCT_CATEGORY = "productCategory"
    
    #: String: Range of years to maturity
    YEARS_TO_MATURITY = "yearsToMaturity"
    
    #: String: Run Code
    BENCHMARK = "benchmark"
    
    #: Number: Count of securities for ATS-Interdealer
    ATS_INTERDEALER_TRADES = "atsInterdealerCount"
    
    #: Number: Volume in Dollars for ATS-Interdealer
    ATS_INTERDEALER_VOLUME = "atsInterdealerVolume"
    
    #: Number: Count of securities for Dealer-Customer
    DEALER_CUSTOMER_TRADES = "dealerCustomerCount"
    
    #: Number: Volume in Dollars for Dealer-Customer
    DEALER_CUSTOMER_VOLUME = "dealerCustomerVolume"
    

class WeeklyCMBSPricing(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_weekly_cmbs_pricing`
    """
    
    #: Date: The report date for the IDC pricing data.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: String: The pricing table name from the IDC workbook
    PRICING_TABLE_NAME = "pricingTableName"
    
    #: String: The CMBS product type code
    PRODUCT_CODE = "productCode"
    
    #: String: The vintage year code for the CMBS tranche
    VINTAGE_CODE = "vintageCode"
    
    #: String: The pricing category code (e.g., price, yield, spread)
    CATEGORY_CODE = "categoryCode"
    
    #: String: The pricing sub-category code providing additional
    #: classification
    SUB_CATEGORY_CODE = "subCategoryCode"
    
    #: Number: The numeric value for the given pricing category
    VALUE_AMOUNT = "valueAmount"
    
    #: Date: Start of date range data is valid for.
    #: Format: yyyy-MM-dd
    START_ASOF_DATE = "startAsofDate"
    
    #: Date: End of date range data is valid for.
    #: Format: yyyy-MM-dd
    END_ASOF_DATE = "endAsofDate"
    
    #: Datetime: The timestamp when the record was loaded into the database.
    #: Format: yyyy-MM-dd HH:mm:ss.SSSSSS
    RECORD_LOAD_TIMESTAMP = "recordLoadTimestamp"


##########################################################################
# FINRA GROUP

class FINRARulebook(Enum):
    """Fields returned by :py:meth:`BaseClient.get_finra_rulebook`"""
    
    #: String: **Partition Field**. Rule Number.
    RULE_NUMBER = "ruleNumber"
    
    #: Date: Effective start date.
    #: Format: yyyy-MM-dd
    EFFECTIVE_START_DATE = "effectiveStartDate"
    
    #: Date: Effective end date.
    #: Format: yyyy-MM-dd
    EFFECTIVE_END_DATE = "effectiveEndDate"
    
    #: String: Rule Text Ascii
    RULE_TEXT_ASCII = "ruleTextAscii"
    
    #: String: Rule Text Html
    RULE_TEXT_HTML = "ruleTextHtml"
    
    #: String: The title of the rule
    RULE_TITLE = "ruleTitle"
    
    #: String: The position of the rule in the rulebook hierarchy
    RULEBOOK_HIERARCHY = "rulebookHierarchy"
    
    #: Array<String>: List of high-level fundamental regulatory topics
    #: associated with the rule
    SUMMARY_TOPICS = "summaryTopics"
    
    #: Array<String>: List of comprehensive topics, regulatory or otherwise,
    #: associated with the rule
    DETAILED_TOPICS = "detailedTopics"


class FirmsRegistrationTypes(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_firm_registration_types`
    """
    
    #: Date: **Partition Field**. Year-end for which Industry Snapshot
    #: statistics were compiled.
    #: Format: yyyy-MM-dd
    REPORT_DATE = "reportDate"
    
    #: Number: Year for which the statistic applies
    YEAR = "year"
    
    #: String: Record identifier that specifies whether it is a firm or
    #: individual record
    INDIVIDUAL_OR_FIRM = "individualOrFirm"
    
    #: String: Type of registration
    REGISTRATION_TYPE_AT_END_OF_YEAR = "registrationTypeAtEndOfYear"
    
    #: Number: Number of firms with a particular type of registration
    NUMBER_OF_FIRMS = "numberOfFirms"


##########################################################################
# FIRM GROUP

class FirmCustomerComplaints(Enum):
    """
    Fields returned by :py:meth:`BaseClient.get_firm_customer_complaints`
    """
    
    #: Number: Filing Number
    FILING_NUMBER = "filingNumber"
    
    #: Number: Version Number
    VERSION_NUMBER = "versionNumber"
    
    #: String: Filing Type Code
    FILING_TYPE_CODE = "filingTypeCode"
    
    #: String: Filing Status
    FILING_STATUS = "filingStatus"
    
    #: String: Firm Sequence Number
    FIRM_SEQUENCE_NUMBER = "firmSequenceNumber"
    
    #: Datetime: Submission Datetime.
    #: Format: yyyy-MM-dd HH:mm:ss.SSS
    SUBMISSION_DATETIME = "submissionDate"
    
    #: Number: Firm CRD Number
    FIRM_CRD_NUMBER = "firmCrdNumber"
    
    #: String: Event Code
    EVENT_CODE = "eventCode"
    
    #: String: Alleged Activity Period Date 1
    ALLEGED_ACTIVITY_PERIOD_DATE1 = "allegedActivityPeriodDate1"
    
    #: String: Alleged Activity Period Date Flag 1
    ALLEGED_ACTIVITY_PERIOD_DATE_FLAG1 = "allegedActivityPeriodDateFlag1"
    
    #: String: Alleged Activity Period Date 2
    ALLEGED_ACTIVITY_PERIOD_DATE2 = "allegedActivityPeriodDate2"
    
    #: String: Alleged Activity Period Date Flag 2
    ALLEGED_ACTIVITY_PERIOD_DATE_FLAG2 = "allegedActivityPeriodDateFlag2"
    
    #: Datetime: Discovery Datetime.
    #: Format: yyyy-MM-dd HH:mm:ss.SSS
    DISCOVERY_DATETIME = "discoveryDate"
    
    #: String: Complaint Related To Representative Flag
    COMPLAINT_RELATED_TO_REPRESENTATIVE_FLAG = \
        "complaintRelatedToRepresentativeFlag"
    
    #: String: Complaint Related to Firm Flag
    COMPLAINT_RELATED_TO_FIRM_FLAG = "complaintRelatedToFirmFlag"
    
    #: String: Complaint Related to Affiliate Flag
    COMPLAINT_RELATED_TO_AFFILIATE_FLAG = "complaintRelatedToAffiliateFlag"
    
    #: String: Complaint Related to Other Flag
    COMPLAINT_RELATED_TO_OTHER_FLAG = "complaintRelatedToOtherFlag"
    
    #: String: Complaint Related to Account Payable Flag
    COMPLAINT_RELATED_TO_ACCOUNTS_PAYABLE_FLAG = \
        "complaintRelatedToAccountsPayableFlag"
    
    #: String: Complaint Related to Municipal Flag
    COMPLAINT_RELATED_TO_MUNICIPAL_FLAG = "complaintRelatedToMunicipalFlag"
    
    #: String: Branch CRD Number
    BRANCH_CRD_NUMBER = "branchCrdNumber"
    
    #: String: Branch State Code
    BRANCH_STATE_CODE = "branchStateCode"
    
    #: Number: Representative CRD Number
    REPRESENTATIVE_CRD_NUMBER = "representativeCrdNumber"
    
    #: String: Representative City
    REPRESENTATIVE_CITY = "representativeCity"
    
    #: String: Representative Employment Status Code
    REPRESENTATIVE_EMPLOYMENT_STATE_CODE = "representativeEmploymentStateCode"
    
    #: Number: Representative Zip Code Number
    REPRESENTATIVE_ZIP_CODE_NUMBER = "representativeZipCodeNumber"
    
    #: String: Representative Supervisor FirstName
    REPRESENTATIVE_SUPERVISOR_FIRST_NAME = "representativeSupervisorFirstName"
    
    #: String: Representative Supervisor LastName
    REPRESENTATIVE_SUPERVISOR_LAST_NAME = "representativeSupervisorLastName"
    
    #: String: Problem Code
    PROBLEM_CODE = "problemCode"
    
    #: String: Product Code
    PRODUCT_CODE = "productCode"
    
    #: String: Customer First Name
    CUSTOMER_FIRST_NAME = "customerFirstName"
    
    #: String: Customer Last Name
    CUSTOMER_LAST_NAME = "customerLastName"
    
    #: String: Disputed Amount Indicator
    DISPUTED_AMOUNT_INDICATOR = "disputedAmountIndicator"
    
    #: String: DispositionCode
    DISPOSITION_CODE = "dispositionCode"
    
    #: Number: Total Disputed Amount
    TOTAL_DISPUTED_AMOUNT = "totalDisputedAmount"
    
    #: String: Security Symbol 1
    SECURITY_SYMBOL1 = "securitySymbol1"
    
    #: String: Security Description 1
    SECURITY_DESCRIPTION1 = "securityDescription1"
    
    #: String: Security Symbol 2
    SECURITY_SYMBOL2 = "securitySymbol2"
    
    #: String: Security Description 2
    SECURITY_DESCRIPTION2 = "securityDescription2"
    
    #: String: Security Symbol 3
    SECURITY_SYMBOL3 = "securitySymbol3"
    
    #: String: Security Description 3
    SECURITY_DESCRIPTION3 = "securityDescription3"
    
    #: String: Disciplinary Action Code
    DISCIPLINARY_ACTION_CODE = "disciplinaryActionCode"
    
    #: String: Investigator First Name
    INVESTIGATOR_FIRST_NAME = "investigatorFirstName"
    
    #: String: Investigator Last Name
    INVESTIGATOR_LAST_NAME = "investigatorLastName"
    
    #: Datetime: Response Datetime.
    #: Format: yyyy-MM-dd HH:mm:ss.SSS
    RESPONSE_DATETIME = "responseDate"
    
    #: String: Statutory Disqualification Party First Name
    STATUTORY_DISQUALIFICATION_PARTY_FIRST_NAME = \
        "statutoryDisqualificationPartyFirstName"
    
    #: String: Statutory Disqualification Party Last Name
    STATUTORY_DISQUALIFICATION_PARTY_LAST_NAME = \
        "statutoryDisqualificationPartyLastName"
    
    #: String: Statutory Disqualification Party Company Name
    STATUTORY_DISQUALIFICATION_PARTY_COMPANY_NAME = \
        "statutoryDisqualificationPartyCompanyName"
    
    #: String: Statutory Disqualifications Member Relation Code
    STATUTORY_DISQUALIFICATIONS_MEMBER_RELATION_CODE = \
        "statutoryDisqualificationsMemberRelationCode"
    
    #: String: Comment Summary
    COMMENT_SUMMARY = "commentSummary"
    
    #: String: Comment
    COMMENT = "comment"
    
    #: String: Contact First Name
    CONTACT_FIRST_NAME = "contactFirstName"
    
    #: String: Contact Last Name
    CONTACT_LAST_NAME = "contactLastName"
    
    #: String: Contact Telephone Number
    CONTACT_TELEPHONE_NUMBER = "contactTelephoneNumber"
    
    #: String: Explanation
    EXPLANATION = "explanation"
    
    #: String: Subjects Name
    SUBJECTS_NAME = "subjectsName"
    
    #: String: Other Party Name
    OTHER_PARTY_NAME = "otherPartyName"
    
    #: Datetime: Transaction Datetime.
    #: Format: yyyy-MM-dd HH:mm:ss.SSS
    TRANSACTION_DATETIME = "transactionDate"
    
    #: Number: Transaction Amount
    TRANSACTION_AMOUNT = "transactionAmount"
    
    #: Datetime: Transaction Datetime 2.
    #: Format: yyyy-MM-dd HH:mm:ss.SSS
    TRANSACTION_DATETIME_2 = "transactionDate2"
    
    #: String: Filing Period
    FILING_PERIOD = "filingPeriod"
    
    #: String: Branch ZIP Code
    BRANCH_POSTAL_CODE = "branchPostalCode"


class FirmDisclosures(Enum):
    """Fields returned by :py:meth:`BaseClient.get_firm_disclosures`"""
    
    #: Number: The CRD number of a firm
    FIRM_CRD_NUMBER = "firmCrdNumber"
    
    #: String: This indicates the type of disclosure as defined on the filing.
    #: This field is critical during Disclosure Review to help
    #: determine matches to existing occurrences.
    DISCLOSURE_TYPE = "disclosures.disclosureType"
    
    #: Number: Uniquely identifies a disclosure event. Occurrences are created
    #: during the Disclosure Review process so that multiple DRPs can
    #: be related to a single event.
    OCCURRENCE_NUMBER = "disclosures.occurrenceNumber"
    
    #: String: This indicates an occurrence determined to be reportable via
    #: Forms BD and/or ADV.
    REPORTABLE_FLAG = "disclosures.reportableFlag"
    
    #: String: This indicates whether or not an occurrence is disclosed through
    #: the FINRA BrokerCheck program.
    DISCLOSABLE_FLAG = "disclosures.disclosableFlag"
    
    #: String: Is Disclosure Archived?
    ARCHIVED_FLAG = "disclosures.archivedFlag"
    
    #: Date: The date on which this event occurred.
    #: Format: yyyy-MM-dd
    EVENT_DATE = "disclosures.eventDate"
    
    #: String: The Regulator code associated to the registration
    REGULATOR_CODE = "registrations.regulatorCode"


class FirmProfile(Enum):
    """Fields returned by :py:meth:`BaseClient.get_firm_profile`"""
    
    #: Number: The CRD number of a firm
    FIRM_CRD_NUMBER = "firmCrdNumber"
    
    #: String: The firm name
    DOING_BUSINESS_AS_NAME = "doingBusinessAsName"
    
    #: String: The firm applicant name of an branch
    FIRM_APPLICANT_NAME = "firmApplicantName"
    
    #: String: The type code for the registered firm
    REGISTERED_FIRM_TYPE_CODE = "registeredFirmTypeCode"
    
    #: String: The SEC 802 number of the firm
    SEC802_FIRM_IDENTIFIER = "sec802FirmIdentifier"
    
    #: String: The SEC 801 number of the firm
    SEC801_FIRM_IDENTIFIER = "sec801FirmIdentifier"
    
    #: String: The SEC 8 number of the firm
    SEC8_FIRM_IDENTIFIER = "sec8FirmIdentifier"
    
    #: String: The FINRA district of the firm
    FIRM_FINRA_DISTRICT = "firmFinraDistrict"
    
    #: String: Address line 1 of a location
    ADDRESS_LINE1 = "firmAddress.addressLine1"
    
    #: String: Address line 2 of a location
    ADDRESS_LINE2 = "firmAddress.addressLine2"
    
    #: String: City name of a location
    CITY_NAME = "firmAddress.cityName"
    
    #: String: State code of a location
    STATE_CODE = "firmAddress.stateCode"
    
    #: String: State name of a location
    STATE_NAME = "firmAddress.stateName"
    
    #: String: Country code of a location
    COUNTRY_CODE = "firmAddress.countryCode"
    
    #: String: Country name of a location
    COUNTRY_NAME = "firmAddress.countryName"
    
    #: String: Postal code of a location
    POSTAL_CODE = "firmAddress.postalCode"
    
    #: String: The Regulator code associated to the registration
    REGULATOR_CODE = "registrations.regulatorCode"


class FirmRegistrationStatusHistory(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_firm_registration_status_history`
    """
    
    #: Number: The CRD number of a firm
    FIRM_CRD_NUMBER = "firmCrdNumber"
    
    #: String: The Regulator code associated to the registration
    REGULATOR_CODE = "registrationStatusHistory.regulatorCode"
    
    #: String: The regulator name associated to the registration
    REGULATOR_NAME = "registrationStatusHistory.regulatorName"
    
    #: Date: The notice date of registration status.
    #: Format: yyyy-MM-dd
    NOTICE_DATE = "registrationStatusHistory.noticeDate"
    
    #: String: The notice reason for the firm registration status
    NOTICE_REASON = "registrationStatusHistory.noticeReason"
    
    #: String: The status name of the firm registration
    STATUS_NAME = "registrationStatusHistory.statusName"
    
    #: String: The status code of the firm registration
    STATUS_CODE = "registrationStatusHistory.statusCode"


class FirmRegistrations(Enum):
    """Fields returned by :py:meth:`BaseClient.get_firm_registrations`"""
    
    #: Number: The CRD number of a firm
    FIRM_CRD_NUMBER = "firmCrdNumber"
    
    #: String: The Regulator code associated to the registration
    REGULATOR_CODE = "registrations.regulatorCode"
    
    #: String: The regulator name associated to the registration
    REGULATOR_NAME = "registrations.regulatorName"
    
    #: String: Registration category business type; Broker-Dealer (BD) ,
    #: Investment Adviser (IA)
    REGISTRATION_TYPE = "registrations.registrationType"
    
    #: String: The status code of the firm registration
    STATUS_NAME = "registrations.statusName"
    
    #: String: The status code of the firm registration
    STATUS_CODE = "registrations.statusCode"
    
    #: Date: The effective date of the current status.
    #: Format: yyyy-MM-dd
    EFFECTIVE_DATE = "registrations.effectiveDate"
    
    #: String: Is this the current registration status?
    IS_CURRENT = "registrations.isCurrent"


##########################################################################
# REGISTRATION GROUP

class CompositeBranchSections(Enum):
    """Sections returned by :py:meth:`BaseClient.get_composite_branch`"""
    
    #: Registrations
    REGISTRATIONS = "registrations"
    
    #: Cleared Deficiencies
    CLEARED_DEFICIENCIES = "clearedDeficiencies"
    
    #: General Information includes the following sections:
    #:  - "financialActivity"
    #:  - "records"
    #:  - "identifyingInformation"
    #:  - "otherBusiness"
    #:  - "location"
    #:  - "arrangements"
    #:  - "status"
    GENERAL_INFORMATION = "generalInformation"
    
    #: Deficiencies
    DEFICIENCIES = "deficiencies"
    
    #: Individuals
    INDIVIDUALS = "individuals"


class CompositeIndividualSections(Enum):
    """
    Sections returned by both :py:meth:`BaseClient.get_composite_individual`
    and :py:meth:`BaseClient.get_composite_individual_seed`
    """
    
    #: Annual CE
    ANNUAL_CONTINUING_EDUCATION = "AnnualContinuingEducation"
    
    #: IA CE
    INVESTMENT_ADVISOR_CONTINUING_EDUCATION = \
        "InvestmentAdviserContinuingEducation"
    
    #: Disclosure Occurrences
    OCCURRENCES = "occurrences"
    
    #: Filing Events
    EVENTS = "events"
    
    #: Exam History
    EXAMS = "exams"
    
    #: Firm Associations
    FIRM_ASSOCIATIONS = "firmAssociations"
    
    #: Individual Information
    INDIVIDUAL = "individual"


class IndividualPreRegistrationSearch(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_individual_pre_registration_search`
    """
    
    #: Number: The CRD number of an individual
    INDIVIDUAL_CRD_NUMBER = "individualCrdNumber"
    
    #: String: Individual's primary first name
    FIRST_NAME = "firstName"
    
    #: String: Individual's primary middle name
    MIDDLE_NAME = "middleName"
    
    #: String: Individual's primary last name
    LAST_NAME = "lastName"
    
    #: String: Individual's primary suffix
    SUFFIX_NAME = "suffixName"
    
    #: String: The individual’s statutory disqualification status or type if
    #: the individual is associated in any business or financial
    #: activity with any person who is subject to a statutory
    #: disqualification.
    STATUTORY_DISQUALIFICATION_CODE = "statutoryDisqualificationCode"
    
    #: String: This flag indicates whether individual's CE requirement has been
    #: deferred due to military service.
    MILITARY_DEFERRED_FLAG = "militaryDeferredFlag"
    
    #: Date: When the individual’s statutory disqualification became effective.
    #: Format: yyyy-MM-dd
    STATUTORY_DISQUALIFICATION_STATUS_DATE = \
        "statutoryDisqualificationStatusDate"
    
    #: String: Code for the individual’s country of birth
    PERSONAL_INFORMATION_COUNTRY_OF_BIRTH_CODE = \
        "personalInformation.countryOfBirthCode"
    
    #: String: Code for the individual’s state of birth
    PERSONAL_INFORMATION_STATE_OF_BIRTH_CODE = \
        "personalInformation.stateOfBirthCode"
    
    #: String: Code for the individual’s state or province of birth
    PERSONAL_INFORMATION_STATE_PROVINCE_OF_BIRTH_CODE = \
        "personalInformation.stateProvinceOfBirthCode"
    
    #: String: Uniquely identifier of a disclosure event. Occurrences numbers
    #: are created during the disclosure review process and as such,
    #: multiple DRPs can be related to a single event.
    DISCLOSURES_OCCURRENCE_NUMBER = "disclosures.occurrenceNumber"
    
    #: String: Code that defines the type of disclosure
    DISCLOSURES_DISCLOSURE_TYPE_CODE = "disclosures.disclosureTypeCode"
    
    #: String: This indicates whether or not the occurrence is reportable. The
    #: setting on this field is used in VOI to determine if and where
    #: (Current Disclosures or Reg Archive Disclosures) the occurrence
    #: should be displayed.
    DISCLOSURES_REPORTABLE_FLAG = "disclosures.reportableFlag"
    
    #: String: This flag indicates whether the record is Eligible for Public
    #: Disclosure. This applies to Archived Disclosures and indicates
    #: whether or not an archived, customer complaint/arbitration/civil
    #: litigation occurrence may be eligible to be disclosed through
    #: the FINRA BrokerCheck Program.
    DISCLOSURES_PUBLICLY_DISCLOSABLE_FLAG = \
        "disclosures.publiclyDisclosableFlag"
    
    #: String: Reason for archiving
    DISCLOSURES_ARCHIVE_REASON_TYPE = "disclosures.archiveReasonType"

    #: String: List of disclosure questions answered yes
    DISCLOSURES_QUESTION_ANSWERED_TEXT = "disclosures.questionAnsweredText"
    
    #: Date: When the event that required disclosure occurred.
    #: Format: yyyy-MM-dd
    DISCLOSURES_EVENT_DATE = "disclosures.eventDate"
    
    #: Date: When the event that required disclosure occurred.
    #: Format: yyyy-MM-dd
    DISCLOSURE_FILINGS_EVENT_DATE = "disclosureFilings.eventDate"
    
    #: String: Code for the type of form on which the disclosure was submitted.
    #: Possible values:
    #:
    #: - ``U4``
    #: - ``U5``
    #: - ``U6``
    #: - ``BD``
    DISCLOSURE_FILINGS_FORM_TYPE_CODE = "disclosureFilings.formTypeCode"
    
    #: Number: Unique number through which all records related to a particular
    #: filing are identified
    DISCLOSURE_FILINGS_FILING_NUMBER = "disclosureFilings.filingNumber"
    
    #: Date: The filing date for the form filing ID associated with the
    #: disclosure.
    #: Format: yyyy-MM-dd
    DISCLOSURE_FILINGS_FILING_DATE = "disclosureFilings.filingDate"
    
    #: Number: The Code of the regulator that submitted the Filing on which the
    #: disclosure was reported
    DISCLOSURE_FILINGS_FILED_BY_REGULATOR_CODE = \
        "disclosureFilings.filedByRegulatorCode"
    
    #: Number: The CRD number of the organization that submitted the Filing on
    #: which the disclosure was reported
    DISCLOSURE_FILINGS_FILED_BY_FIRM_CRD_NUMBER = \
        "disclosureFilings.filedByFirmCrdNumber"
    
    #: String: Uniquely identifier of a disclosure event. Occurrences numbers
    #: are created during the disclosure review process and as such,
    #: multiple DRPs can be related to a single event.
    DISCLOSURE_FILINGS_OCCURRENCE_NUMBER = "disclosureFilings.occurrenceNumber"
    
    #: String: The individual's other first name
    OTHER_NAMES_FIRST_NAME = "otherNames.firstName"
    
    #: String: The individual's other last name
    OTHER_NAMES_LAST_NAME = "otherNames.lastName"
    
    #: String: The individual's other middle name
    OTHER_NAMES_MIDDLE_NAME = "otherNames.middleName"
    
    #: String: The individual's other suffix
    OTHER_NAMES_SUFFIX_NAME = "otherNames.suffixName"
    
    #: String: Flag to indicate if the individual conducts business outside of
    #: the registered firm
    OUTSIDE_BUSINESS_FLAG = "outsideBusinessFlag"
    
    #: String: This describes the business conducted by the individual outside
    #: of the registered firm. It includes: the name and address of the
    #: other business; the nature of the other business, including
    #: whether it is investmentrelated; the position, title, or
    #: association with the other business, including duties; the start
    #: date of the relationship with the other business; the
    #: approximate number of hours per month devoted to the other
    #: business; and the number of hours devoted to the other business
    #: during securities trading hours.
    OTHER_BUSINESS = "otherBusiness"
    
    #: String: Identifies the type of IA affiliation
    INVESTMENT_ADVISOR_AFFILIATIONS_AFFILIATION_TYPE = \
        "investmentAdvisorAffiliations.affiliationType"
    
    #: String: The CRD ID for the affiliated IA firm
    INVESTMENT_ADVISOR_AFFILIATIONS_AFFILIATION_FIRM_CRD_NUMBER = \
        "investmentAdvisorAffiliations.affiliationFirmCrdNumber"
    
    #: String: The name of the affiliated IA firm
    INVESTMENT_ADVISOR_AFFILIATIONS_AFFILIATION_FIRM_NAME = \
        "investmentAdvisorAffiliations.affiliationFirmName"
    
    #: String: The individual's professional designation type code
    PROFESSIONAL_DESIGNATIONS_DESIGNATION_TYPE_CODE = \
        "professionalDesignations.designationTypeCode"
    
    #: String: The individual's professional designation type name
    PROFESSIONAL_DESIGNATIONS_DESIGNATION_TYPE_NAME = \
        "professionalDesignations.designationTypeName"
    
    #: String: The name of the organization that grants the professional
    #: designation to the individual e.g. CFP awarded by Certified
    #: Financial Planner Board of Standards.
    PROFESSIONAL_DESIGNATIONS_DESIGNATION_AUTHORITY_NAME = \
        "professionalDesignations.designationAuthorityName"
    
    #: Date: The date of the first filing of the individual's professional
    #: designation.
    #: Format: yyyy-MM-dd
    PROFESSIONAL_DESIGNATIONS_FIRST_FILING_DATE = \
        "professionalDesignations.firstFilingDate"
    
    #: Date: The date of the most recent filing of the individual's
    #: professional designation.
    #: Format: yyyy-MM-dd
    PROFESSIONAL_DESIGNATIONS_LAST_FILING_DATE = \
        "professionalDesignations.lastFilingDate"
    
    #: String: The type of form used for the last filing
    PROFESSIONAL_DESIGNATIONS_FIRST_FILING_TYPE = \
        "professionalDesignations.firstFilingType"
    
    #: String: The type of last filing of the designation
    PROFESSIONAL_DESIGNATIONS_LAST_FILING_TYPE = \
        "professionalDesignations.lastFilingType"
    
    #: String: The code for the form U4 filing type that lists the designation
    #: of the individual
    PROFESSIONAL_DESIGNATIONS_FIRST_FORM_TYPE_CODE = \
        "professionalDesignations.firstFormTypeCode"
    
    #: String: The type of form used for the last filing in which the
    #: designation of the individual is listed
    PROFESSIONAL_DESIGNATIONS_LAST_FORM_TYPE_CODE = \
        "professionalDesignations.lastFormTypeCode"
    
    #: Date: Start date of individual residency at the address.
    #: Format: yyyy-MM-dd
    RESIDENTIAL_LOCATIONS_ADDRESS_START_DATE = \
        "residentialLocations.addressStartDate"
    
    #: Date: End date of individual residency at the address.
    #: Format: yyyy-MM-dd
    RESIDENTIAL_LOCATIONS_ADDRESS_END_DATE = \
        "residentialLocations.addressEndDate"
    
    #: String: Residence street address – line 1
    RESIDENTIAL_LOCATIONS_ADDRESS_LINE1 = "residentialLocations.addressLine1"
    
    #: String: Residence street address – line 2
    RESIDENTIAL_LOCATIONS_ADDRESS_LINE2 = "residentialLocations.addressLine2"
    
    #: String: Residence city
    RESIDENTIAL_LOCATIONS_CITY_NAME = "residentialLocations.cityName"
    
    #: String: Residence state
    RESIDENTIAL_LOCATIONS_STATE_CODE = "residentialLocations.stateCode"
    
    #: String: Residence postal code
    RESIDENTIAL_LOCATIONS_POSTAL_CODE = "residentialLocations.postalCode"
    
    #: String: Residence country code
    RESIDENTIAL_LOCATIONS_COUNTRY_CODE = "residentialLocations.countryCode"
    
    #: Date: The date the registration filing occurred.
    #: Format: yyyy-MM-dd
    REGISTRATIONS_FILING_DATE = "registrations.filingDate"
    
    #: String: The code for the registered individual's position
    REGISTRATIONS_REGISTRATION_CATEGORY_CODE = \
        "registrations.registrationCategoryCode"
    
    #: String: Individual's registration status code
    REGISTRATIONS_REGISTRATION_STATUS_CODE = \
        "registrations.registrationStatusCode"
    
    #: Date: The date the registration began.
    #: Format: yyyy-MM-dd
    REGISTRATIONS_REGISTRATION_BEGIN_DATE = \
        "registrations.registrationBeginDate"
    
    #: Date: The date the individual's registration ended.
    #: Format: yyyy-MM-dd
    REGISTRATIONS_REGISTRATION_END_DATE = "registrations.registrationEndDate"
    
    #: Date: The date the registration became effective.
    #: Format: yyyy-MM-dd
    REGISTRATIONS_STATUS_EFFECTIVE_DATE = "registrations.statusEffectiveDate"
    
    #: String: The regulator code assigned to the individual's registrationn
    REGISTRATIONS_REGULATOR_CODE = "registrations.regulatorCode"
    
    #: Number: CRD number of firm associated with the deficiency
    DEFICIENCIES_FIRM_CRD_NUMBER = "deficiencies.firmCrdNumber"
    
    #: String: The specific exam codes if the deficiency type is Exam
    DEFICIENCIES_EXAM_CODE = "deficiencies.examCode"
    
    #: String: The registration category associated with registration
    #: deficiency
    DEFICIENCIES_REGISTRATION_CATEGORY_CODE = \
        "deficiencies.registrationCategoryCode"
    
    #: String: Regulator code for the regulator associated with the
    #: registration deficiency
    DEFICIENCIES_REGULATOR_CODE = "deficiencies.regulatorCode"
    
    #: String: Flag the indicates whether a deficiency has been cleared
    DEFICIENCIES_DEFICIENCY_CLEARED = "deficiencies.deficiencyCleared"
    
    #: String: Detailed description of the deficiency
    DEFICIENCIES_DEFICIENCY_DESCRIPTION = "deficiencies.deficiencyDescription"
    
    #: Date: Date when the deficiency was cleared.
    #: Format: yyyy-MM-dd
    DEFICIENCIES_REGISTRATION_DEFICIENCY_CLEARED_DATE = \
        "deficiencies.registrationDeficiencyClearedTimestamp"
    
    #: Date: Date when the record of the deficiency was created.
    #: Format: yyyy-MM-dd
    DEFICIENCIES_REGISTRATION_DEFICIENCY_CREATED_DATE = \
        "deficiencies.registrationDeficiencyCreatedTimestamp"
    
    #: String: Employing firm's CRD number
    EMPLOYMENTS_FIRM_CRD_NUMBER = "employments.firmCrdNumber"
    
    #: String: Flag to indicated whether the individual’s employment is active
    #: or not
    EMPLOYMENTS_IS_ACTIVE = "employments.isActive"
    
    #: String: The billing code associated with the individual
    EMPLOYMENTS_INDIVIDUAL_BILLING_CODE = "employments.individualBillingCode"
    
    #: Date: Date employment started.
    #: Format: yyyy-MM-dd
    EMPLOYMENTS_EMPLOYMENT_START_DATE = "employments.employmentStartDate"
    
    #: Date: Date employment ended.
    #: Format: yyyy-MM-dd
    EMPLOYMENTS_EMPLOYMENT_END_DATE = "employments.employmentEndDate"
    
    #: String: Employment Type Code
    EMPLOYMENTS_EMPLOYMENT_TYPE_CODE = "employments.employmentTypeCode"
    
    #: String: Flag indicating whether the person is an independent contractor
    EMPLOYMENTS_INDEPENDENT_CONTRACTOR_FLAG = \
        "employments.independentContractorFlag"
    
    #: String: This is the description of the reason for termination.
    EMPLOYMENTS_TERMINATION_REASON_DESCRIPTION = \
        "employments.terminationReasonDescription"
    
    #: String: This is the explanation of the reason for termination.
    EMPLOYMENTS_TERMINATION_REASON_EXPLANATION = \
        "employments.terminationReasonExplanation"
    
    #: String: Flag indicating that the individual is registered as an
    #: investment advisor with two unaffiliated firms
    EMPLOYMENTS_DUAL_INVESTMENT_ADVISOR_FLAG = \
        "employments.dualInvestmentAdvisorFlag"
    
    #: String: Address line 1 of a location
    FIRM_ADDRESS_ADDRESS_LINE1 = "employments.firmAddress.addressLine1"
    
    #: String: Address line 2 of a location
    FIRM_ADDRESS_ADDRESS_LINE2 = "employments.firmAddress.addressLine2"
    
    #: String: City name of a location
    FIRM_ADDRESS_CITY_NAME = "employments.firmAddress.cityName"
    
    #: String: State name of a location
    FIRM_ADDRESS_STATE_NAME = "employments.firmAddress.stateName"
    
    #: String: Postal code of a location
    FIRM_ADDRESS_POSTAL_CODE = "employments.firmAddress.postalCode"
    
    #: String: Name of the firm
    EMPLOYMENTS_FIRM_NAME = "employments.firmName"
    
    #: String: CRD number of the registered branch
    BRANCH_OFFICE_LOCATIONS_BRANCH_CRD_NUMBER = \
        "branchOfficeLocations.branchCrdNumber"
    
    #: String: CRD number of the non-registered branch
    BRANCH_OFFICE_LOCATIONS_NON_REGISTERED_BRANCH_IDENTIFIER = \
        "branchOfficeLocations.nonRegisteredBranchIdentifier"
    
    #: String: Firm CRD Number
    BRANCH_OFFICE_LOCATIONS_FIRM_CRD_NUMBER = \
        "branchOfficeLocations.firmCrdNumber"
    
    #: String: Flag to denote whether the branch is a registered location or
    #: not
    BRANCH_OFFICE_LOCATIONS_REGISTERED_LOCATION_FLAG = \
        "branchOfficeLocations.registeredLocationFlag"
    
    #: String: Branch street address – line 1
    BRANCH_ADDRESS_ADDRESS_LINE1 = \
        "branchOfficeLocations.branchAddress.addressLine1"
    
    #: String: Branch street address – line 2
    BRANCH_ADDRESS_ADDRESS_LINE2 = \
        "branchOfficeLocations.branchAddress.addressLine2"
    
    #: String: Branch city name
    BRANCH_ADDRESS_CITY_NAME = "branchOfficeLocations.branchAddress.cityName"
    
    #: String: Branch state code
    BRANCH_ADDRESS_STATE_CODE = "branchOfficeLocations.branchAddress.stateCode"
    
    #: String: Branch postal code
    BRANCH_ADDRESS_POSTAL_CODE = \
        "branchOfficeLocations.branchAddress.postalCode"
    
    #: String: Branch country
    BRANCH_ADDRESS_COUNTRY_CODE = \
        "branchOfficeLocations.branchAddress.countryCode"
    
    #: String: Branch type indicator
    BRANCH_OFFICE_LOCATIONS_OFFICE_LOCATION_TYPE = \
        "branchOfficeLocations.officeLocationType"
    
    #: Date: The date individual started working at the branch office.
    #: Format: yyyy-MM-dd
    BRANCH_OFFICE_LOCATIONS_OFFICE_LOCATION_START_DATE = \
        "branchOfficeLocations.officeLocationStartDate"
    
    #: Date: The date individual stopped working at the branch office.
    #: Format: yyyy-MM-dd
    BRANCH_OFFICE_LOCATIONS_OFFICE_LOCATION_END_DATE = \
        "branchOfficeLocations.officeLocationEndDate"
    
    #: String: The branch billing code
    BRANCH_OFFICE_LOCATIONS_BRANCH_BILLING_CODE = \
        "branchOfficeLocations.branchBillingCode"
    
    #: String: Flag to indicate whether the branch location is a private
    #: residence
    BRANCH_OFFICE_LOCATIONS_PRIVATE_RESIDENCE_FLAG = \
        "branchOfficeLocations.privateResidenceFlag"
    
    #: String: The name of the non-investment related organization that
    #: employed the individual
    NON_INDUSTRY_EMPLOYMENTS_FIRM_NAME = "nonIndustryEmployments.firmName"
    
    #: Date: Date employment started at an organization that is not investment
    #: related.
    #: Format: yyyy-MM-dd
    NON_INDUSTRY_EMPLOYMENTS_EMPLOYMENT_START_DATE = \
        "nonIndustryEmployments.employmentStartDate"
    
    #: Date: Date employment ended at an organization that is not investment
    #: related.
    #: Format: yyyy-MM-dd
    NON_INDUSTRY_EMPLOYMENTS_EMPLOYMENT_END_DATE = \
        "nonIndustryEmployments.employmentEndDate"
    
    #: String: Flag to indicated whether the individual is employed by an
    #: organization that is not investment related
    NON_INDUSTRY_EMPLOYMENTS_INVESTMENT_RELATED_INDICATOR = \
        "nonIndustryEmployments.investmentRelatedIndicator"
    
    #: String: Description of the position held by the individual at a
    #: non-investment related organization
    NON_INDUSTRY_EMPLOYMENTS_POSITION_DESCRIPTION = \
        "nonIndustryEmployments.positionDescription"
    
    #: String: Name of the city where the non-investment related firm that
    #: employed the individual is located
    ADDRESS_CITY_NAME = "nonIndustryEmployments.address.cityName"
    
    #: String: Code for the state where the non-investment related firm that
    #: employed the individual is located
    ADDRESS_STATE_CODE = "nonIndustryEmployments.address.stateCode"
    
    #: String: The current CE status associated with an individual
    CE_STATUS = "ceStatus"
    
    #: Date: The date associated with current CE Status.
    #: Format: yyyy-MM-dd
    CE_STATUS_DATE = "ceStatusDate"
    
    #: Date: The begin date of CE window. The individual is required to
    #: complete the CE starting from this date.
    #: Format: yyyy-MM-dd
    CE_SESSIONS_WINDOW_BEGIN_DATE = "ceSessions.windowBeginDate"
    
    #: Date: The end date of CE window. The individual is required to complete
    #: the CE by this date.
    #: Format: yyyy-MM-dd
    CE_SESSIONS_WINDOW_END_DATE = "ceSessions.windowEndDate"
    
    #: Date: The begin date of next CE window. The individual is required to
    #: complete the next CE starting from this date.
    #: Format: yyyy-MM-dd
    CE_SESSIONS_NEXT_WINDOW_BEGIN_DATE = "ceSessions.nextWindowBeginDate"
    
    #: String: The code for exam grade for the exam completed by the individual
    CE_SESSIONS_GRADE_CODE = "ceSessions.gradeCode"
    
    #: String: The code of the CE session targeted to the particular set of
    #: registrations an individual holds
    CE_SESSIONS_SESSION_TYPE_CODE = "ceSessions.sessionTypeCode"
    
    #: String: This flag indicates whether individual's CE requirement has been
    #: deferred due to military service.
    CE_SESSIONS_MILITARY_DEFERRED_FLAG = "ceSessions.militaryDeferredFlag"
    
    #: String: The CE requirement type
    CE_SESSIONS_REQUIREMENT_TYPE = "ceSessions.requirementType"
    
    #: String: The individual's CE appointment status code
    CE_SESSIONS_APPOINTMENT_STATUS_CODE = "ceSessions.appointmentStatusCode"
    
    #: String: The progress of the individual's CE training
    CE_SESSIONS_APPOINTMENT_PROGRESS = "ceSessions.appointmentProgress"
    
    #: Date: The date individual last accessed online CE for this session.
    #: Format: yyyy-MM-dd
    CE_SESSIONS_ONLINE_LAST_ACCESSED_DATE = "ceSessions.onlineLastAccessedDate"
    
    #: Date: Date from which the individual was CE inactive.
    #: Format: yyyy-MM-dd
    CE_INACTIVE_HISTORY_FROM_DATE = "ceInactiveHistory.fromDate"
    
    #: Date: Date when the individual stopped being CE inactive.
    #: Format: yyyy-MM-dd
    CE_INACTIVE_HISTORY_TO_DATE = "ceInactiveHistory.toDate"
    
    #: Date: The begin date of CE window. The individual is required to
    #: complete the CE starting from this date.
    #: Format: yyyy-MM-dd
    CE_PREVIOUS_REQUIREMENTS_WINDOW_BEGIN_DATE = \
        "cePreviousRequirements.windowBeginDate"
    
    #: Date: The end date of CE window. The individual is required to complete
    #: the CE by this date.
    #: Format: yyyy-MM-dd
    CE_PREVIOUS_REQUIREMENTS_WINDOW_END_DATE = \
        "cePreviousRequirements.windowEndDate"
    
    #: String: Code indicating the Continuing Education (CE) Session Grade
    #: associated with this record
    CE_PREVIOUS_REQUIREMENTS_GRADE_CODE = "cePreviousRequirements.gradeCode"
    
    #: String: Code indicating the Continuing Education (CE) session time
    #: period associated with this record
    CE_PREVIOUS_REQUIREMENTS_CE_SESSION_TIME_PERIOD_CODE = \
        "cePreviousRequirements.ceSessionTimePeriodCode"
    
    #: String: The code of the CE session targeted to the particular set of
    #: registrations an individual holds
    CE_PREVIOUS_REQUIREMENTS_SESSION_TYPE_CODE = \
        "cePreviousRequirements.sessionTypeCode"
    
    #: String: This flag indicates whether individual's CE requirement has been
    #: deferred due to military service.
    CE_PREVIOUS_REQUIREMENTS_MILITARY_DEFERRED_FLAG = \
        "cePreviousRequirements.militaryDeferredFlag"
    
    #: String: The CE requirement type
    CE_PREVIOUS_REQUIREMENTS_REQUIREMENT_TYPE = \
        "cePreviousRequirements.requirementType"
    
    #: Date: The individual's exam appointment date.
    #: Format: yyyy-MM-dd
    EXAMS_APPOINTMENT_DATE = "exams.appointmentDate"
    
    #: String: The individual's exam appointment status code
    EXAMS_APPOINTMENT_STATUS_CODE = "exams.appointmentStatusCode"
    
    #: String: The city where the test center is located
    EXAMS_TEST_CENTER_CITY = "exams.testCenterCity"
    
    #: String: The country where the test center is located
    EXAMS_TEST_CENTER_COUNTRY_NAME = "exams.testCenterCountryName"
    
    #: String: The state where the test center is located
    EXAMS_TEST_CENTER_STATE = "exams.testCenterState"
    
    #: String: The individual's exam appointment test vendor
    EXAMS_VENDOR = "exams.vendor"
    
    #: String: Individual's Proctor exam appointment confirmation number
    EXAMS__CONFIRMATION_NUMBER = "exams.ConfirmationNumber"
    
    #: String: The code for an exam taken by an individual
    EXAMS_EXAM_CODE = "exams.examCode"
    
    #: String: The code for exam grade for the exam completed by the individual
    EXAMS_EXAM_GRADE_CODE = "exams.examGradeCode"
    
    #: String: The status of the exam completed by the individual
    EXAMS_EXAM_STATUS = "exams.examStatus"
    
    #: Date: The date the exam status was created.
    #: Format: yyyy-MM-dd
    EXAMS_EXAM_STATUS_DATE = "exams.examStatusDate"
    
    #: Date: The date the exam was last taken by the individual.
    #: Format: yyyy-MM-dd
    EXAMS_EXAM_TAKEN_DATE = "exams.examTakenDate"
    
    #: String: Flag to indicate if this exam can be included for exam validity
    #: evaluation
    EXAMS_EXAM_VALIDITY_FLAG = "exams.examValidityFlag"
    
    #: String: The validity status for an exam taken by an individual
    EXAMS_EXAM_VALIDITY_STATUS = "exams.examValidityStatus"
    
    #: Date: The validity date for an exam taken by an individual.
    #: Format: yyyy-MM-dd
    EXAMS_EXAM_VALIDITY_UNTIL_DATE = "exams.examValidityUntilDate"
    
    #: String: Unique identifier assigned to the individual taking the exam
    EXAMS_EXAM_PERSON_IDENTIFIER = "exams.examPersonIdentifier"
    
    #: String: The score for the exam completed by the individual
    EXAMS_EXAM_SCORE = "exams.examScore"
    
    #: String: Code indicating the waiver reason type
    EXAMS_WAIVER_REASON_CODE = "exams.waiverReasonCode"
    
    #: String: The name of the waiver reason type
    EXAMS_WAIVER_REASON_NAME = "exams.waiverReasonName"
    
    #: Date: The begin date of exam window. The individual is required to
    #: complete the exams starting from this date.
    #: Format: yyyy-MM-dd
    EXAMS_WINDOW_BEGIN_DATE = "exams.windowBeginDate"
    
    #: Date: The end date of exam window. The individual is required to
    #: complete the exam by this date.
    #: Format: yyyy-MM-dd
    EXAMS_WINDOW_END_DATE = "exams.windowEndDate"


class IndividualRegistrationValidation(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_individual_registration_validation`
    """
    
    #: Number: The CRD number of an individual
    INDIVIDUAL_CRD_NUMBER = "individualCrdNumber"
    
    #: String: Individual's first name
    FIRST_NAME = "firstName"
    
    #: String: Individual's middle name
    MIDDLE_NAME = "middleName"
    
    #: String: Individual's last name
    LAST_NAME = "lastName"
    
    #: String: Individual's suffix name
    SUFFIX_NAME = "suffixName"
    
    #: String: The CRD number of a firm
    FIRM_CRD_NUMBER = "employments.firmCrdNumber"
    
    #: String: Represents the firm name
    DOING_BUSINESS_AS_NAME = "employments.doingBusinessAsName"
    
    #: String: Is employment active?
    IS_ACTIVE = "employments.isActive"
    
    #: String: The regulator name associated to the registration
    REGULATOR_NAME = "registrations.regulatorName"
    
    #: String: Is registration inactive or suspendeed?
    IS_INACTIVE_OR_SUSPENDED = "registrations.isInactiveOrSuspended"
    
    #: String: Indicates whether the registration held by the individual is as
    #: BrokerDealer or Investment Advisor
    REG_SCOPE = "registrations.regScope"
    
    #: String: Registration Date
    REG_DATE = "registrations.regDate"
    
    #: String: Registration Status
    STATUS = "registrations.status"
    
    #: Array<String>: Registration Categories
    CATEGORIES = "registrations.categories"


class RegisteredIndividualSearch(Enum):
    """
    Fields returned by
    :py:meth:`BaseClient.get_registered_individual_search`
    """
    
    #: Number: The CRD number of an individual
    INDIVIDUAL_CRD_NUMBER = "individualCrdNumber"
    
    #: String: Individual's first name
    FIRST_NAME = "firstName"
    
    #: String: Individual's middle name.
    #: **NOTE:** Field is not in metadata!
    MIDDLE_NAME = "middleName"
    
    #: String: Individual's last name
    LAST_NAME = "lastName"

